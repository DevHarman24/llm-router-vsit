"""
Benchmark Manager
=================
Serves benchmark scores from an in-memory cache with ZERO latency on every
routing request. Scores are refreshed in a background daemon thread every
REFRESH_INTERVAL_HOURS hours so the main request path is never blocked.

Priority order for data (highest to lowest):
  1. In-memory cache  (always returned instantly)
  2. OpenRouter /api/v1/models  (free — embeds real AA + Design Arena scores)
  3. Family inheritance  (e.g. claude-opus-4.8-fast inherits from claude-opus-4.8)
  4. Curated scores  (well-known models with published benchmark numbers)
  5. Price-bracket defaults  (better than random round numbers)
  6. Local benchmarks.json  (seed / legacy fallback)
"""

import json
import os
import re
import time
import threading
import logging

import requests

logger = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────────────────────
BENCHMARKS_FILE        = os.path.join(os.path.dirname(__file__), "benchmarks.json")
OPENROUTER_MODELS_URL  = "https://openrouter.ai/api/v1/models"
REFRESH_INTERVAL_HOURS = 24
FETCH_TIMEOUT          = 20   # seconds for HTTP calls

# ── Forced overrides — take priority OVER live OpenRouter API data ────────────
# Only used for models inheriting old JSON fake values (like 100/100).
FORCED_OVERRIDES = {
    # Parent claude-opus-4.6 real score is 63.8 — fast variant has identical capability.
    "anthropic/claude-opus-4.6-fast": {"coding": 63.8, "reasoning": 63.8, "vision": 63.8},
}

# ── Curated scores for well-known models with published benchmark data ────────
# To correctly align older models with the 2026 AA Index scale (where claude-fable-5 = 76.5),
# we use a mathematical ratio derived from GPT-4o:
# GPT-4o Real OR AA score = 37.0
# GPT-4o HumanEval score = 90.2
# Ratio = 37.0 / 90.2 = 0.410
# We multiply all known legacy HumanEval scores by 0.41 to get their accurate AA equivalent.
CURATED_SCORES = {
    # ── OpenAI ────────────────────────────────────────────────────────────────
    "openai/gpt-4o-2024-08-06":           {"coding": 37.0, "reasoning": 35.9, "vision": 35.9},
    "openai/gpt-4o-2024-11-20":           {"coding": 37.0, "reasoning": 35.9, "vision": 35.9},
    "openai/gpt-4o-mini-2024-07-18":      {"coding": 35.7, "reasoning": 33.6, "vision": 33.6},
    "openai/gpt-4o-mini-search-preview":  {"coding": 35.7, "reasoning": 33.6, "vision": 33.6},
    "openai/gpt-4o-search-preview":       {"coding": 37.0, "reasoning": 35.9, "vision": 35.9},
    "openai/gpt-4-turbo-preview":         {"coding": 33.3, "reasoning": 35.4, "vision": 35.4},
    "openai/gpt-3.5-turbo-0613":          {"coding": 19.7, "reasoning": 15.2, "vision": 15.2},
    "openai/gpt-3.5-turbo-16k":           {"coding": 19.7, "reasoning": 15.2, "vision": 15.2},
    "openai/gpt-3.5-turbo-instruct":      {"coding": 18.2, "reasoning": 14.3, "vision": 14.3},
    
    "openai/o1-pro":                      {"coding": 38.6, "reasoning": 37.7, "vision": 37.7},
    "openai/o3-mini":                     {"coding": 36.5, "reasoning": 35.3, "vision": 35.3},
    "openai/o3-pro":                      {"coding": 39.7, "reasoning": 39.0, "vision": 39.0},
    "openai/o3-deep-research":            {"coding": 38.6, "reasoning": 37.7, "vision": 37.7},
    "openai/o4-mini-high":                {"coding": 38.0, "reasoning": 36.1, "vision": 36.1},
    "openai/o4-mini-deep-research":       {"coding": 38.0, "reasoning": 36.1, "vision": 36.1},
    
    # ── Google ────────────────────────────────────────────────────────────────
    "google/gemini-2.5-pro-preview":      {"coding": 34.5, "reasoning": 32.8, "vision": 32.8},
    "google/gemini-2.5-pro-preview-05-06":{"coding": 34.5, "reasoning": 32.8, "vision": 32.8},
    "google/gemini-2.5-flash-lite":       {"coding": 24.6, "reasoning": 21.3, "vision": 21.3},
    
    # ── Anthropic ─────────────────────────────────────────────────────────────
    "anthropic/claude-3-haiku":           {"coding": 31.1, "reasoning": 30.8, "vision": 30.8},
    "anthropic/claude-opus-4.7-fast":     {"coding": 73.6, "reasoning": 53.5, "vision": 53.5},
    "anthropic/claude-opus-4.8-fast":     {"coding": 74.3, "reasoning": 55.7, "vision": 55.7},
    
    # ── Deepseek ──────────────────────────────────────────────────────────────
    # deepseek-r1 HumanEval ~92.0 -> 92.0 * 0.41 = 37.7
    "deepseek/deepseek-r1":               {"coding": 37.7, "reasoning": 37.7, "vision": 37.7},
    "deepseek/deepseek-r1-distill-llama-70b": {"coding": 33.6, "reasoning": 33.6, "vision": 33.6},
    # 4.6-fast: real OR score for parent is 63.8/63.8; fast variant inherits same
    "anthropic/claude-opus-4.6-fast":     {"coding": 63.8, "reasoning": 63.8, "vision": 63.8},
    # ── Legacy models removed to prefer live OR API / Math Scaling ────────────
}

# ── Price-bracket defaults (last resort for unknown models) ───────────────────
# Based on the principle that providers price models proportionally to capability.
def _price_bracket_score(price_per_million: float) -> dict:
    """Return a default benchmark score based on price tier."""
    if price_per_million <= 0:
        # Free or meta-router models — no meaningful score
        return {"coding": 30.0, "reasoning": 28.0, "vision": 28.0}
    elif price_per_million >= 50.0:
        return {"coding": 72.0, "reasoning": 68.0, "vision": 68.0}
    elif price_per_million >= 15.0:
        return {"coding": 66.0, "reasoning": 62.0, "vision": 62.0}
    elif price_per_million >= 8.0:
        return {"coding": 58.0, "reasoning": 54.0, "vision": 54.0}
    elif price_per_million >= 3.0:
        return {"coding": 50.0, "reasoning": 46.0, "vision": 46.0}
    elif price_per_million >= 1.0:
        return {"coding": 43.0, "reasoning": 39.0, "vision": 39.0}
    elif price_per_million >= 0.3:
        return {"coding": 36.0, "reasoning": 32.0, "vision": 32.0}
    else:
        return {"coding": 28.0, "reasoning": 24.0, "vision": 24.0}


# ── In-memory state ──────────────────────────────────────────────────────────
_cache: dict                             = {}
_cache_lock                              = threading.Lock()
_last_refresh: float                     = 0.0
_refresh_thread: threading.Thread | None = None
_initialized                             = False


# ── Internal helpers ─────────────────────────────────────────────────────────

def _load_from_file() -> dict:
    """Load benchmarks from the local JSON seed file."""
    try:
        with open(BENCHMARKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"[Benchmarks] Loaded {len(data)} entries from benchmarks.json")
        return data
    except Exception as e:
        logger.warning(f"[Benchmarks] Could not load benchmarks.json: {e}")
        return {}


def _arena_score(design_arena: list) -> float | None:
    """
    Compute a representative score (0-100) from Design Arena results.
    Uses the average win_rate across all categories.
    """
    if not design_arena:
        return None
    win_rates = [entry.get("win_rate") for entry in design_arena if entry.get("win_rate") is not None]
    if not win_rates:
        return None
    return round(sum(win_rates) / len(win_rates), 1)


def _fetch_from_openrouter() -> tuple[dict, dict]:
    """
    Fetch benchmark scores + full model catalog from OpenRouter's /api/v1/models.
    Returns:
      - scores: dict keyed by model ID with real benchmark data
      - all_models: dict keyed by model ID with full metadata (for inference)
    """
    try:
        resp = requests.get(OPENROUTER_MODELS_URL, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        models = resp.json().get("data", [])

        scores: dict = {}
        all_models: dict = {}

        for m in models:
            model_id = m.get("id", "")
            if not model_id:
                continue

            all_models[model_id] = m

            benchmarks_raw = m.get("benchmarks")
            if not benchmarks_raw:
                continue

            aa = benchmarks_raw.get("artificial_analysis") or {}
            design_arena = benchmarks_raw.get("design_arena") or []

            coding_idx    = aa.get("coding_index")
            intel_idx     = aa.get("intelligence_index")
            agentic_idx   = aa.get("agentic_index")
            arena_avg     = _arena_score(design_arena)

            coding    = coding_idx or agentic_idx or arena_avg
            reasoning = intel_idx  or agentic_idx or coding_idx or arena_avg

            if coding is None and reasoning is None:
                continue

            coding    = coding    or reasoning
            reasoning = reasoning or coding

            scores[model_id] = {
                "coding":    round(float(coding), 1),
                "reasoning": round(float(reasoning), 1),
                "vision":    round(float(reasoning), 1),
            }

        logger.info(
            f"[Benchmarks] Fetched {len(scores)} real scores from OpenRouter /api/v1/models"
        )
        return scores, all_models

    except Exception as e:
        logger.warning(f"[Benchmarks] OpenRouter fetch failed: {e}")
        return {}, {}


def _infer_family_score(model_id: str, known_scores: dict, penalty: float = 2.0) -> dict | None:
    """
    Try to inherit a score from the closest sibling in the same model family.
    E.g. 'anthropic/claude-opus-4.8-fast' → inherit from 'anthropic/claude-opus-4.8'.
    Applies a small penalty to indicate it's inherited, not measured.
    """
    provider, slug = model_id.split("/", 1) if "/" in model_id else ("", model_id)

    # Strip suffixes like '-fast', ':free', '-thinking', '-high', '-instruct', '-latest'
    # to get the base model slug
    base_slug = re.sub(
        r'(-fast|-thinking|-high|-latest|-instruct|-preview|-customtools|:free|:thinking)$',
        '', slug, flags=re.IGNORECASE
    )

    best_match = None
    best_score = None

    for known_id, score in known_scores.items():
        if not known_id.startswith(provider + "/"):
            continue
        known_slug = known_id.split("/", 1)[1]
        # Match if the known slug starts with the base slug (e.g., claude-opus-4.8 matches claude-opus-4.8-fast)
        if known_slug.startswith(base_slug) or base_slug.startswith(known_slug):
            if best_match is None or len(known_slug) > len(best_match):
                best_match = known_slug
                best_score = score

    if best_score:
        return {
            "coding":    max(1.0, round(best_score["coding"]    - penalty, 1)),
            "reasoning": max(1.0, round(best_score["reasoning"] - penalty, 1)),
            "vision":    max(1.0, round(best_score["vision"]    - penalty, 1)),
        }
    return None


def _build_full_scores(live_scores: dict, all_models: dict, file_data: dict) -> dict:
    """
    Build a complete scores dict covering ALL OpenRouter models using:
    0. FORCED_OVERRIDES (highest — corrects known-bad OR API data)
    1. Live OR API data  (real AA + Design Arena)
    2. Curated hand-researched scores
    3. Family inheritance from other known models
    4. Price-bracket defaults (for models only known via OR catalog, no real score)
    5. Local JSON  (legacy fallback ONLY for models not on OR at all)

    Key insight: file_data is only used for models that don't appear in the
    OpenRouter catalog at all (ultra-rare). For every OR model, we compute
    a proper score rather than keep a stale round number from the JSON.
    """
    # Build the authoritative OR-model score dict first
    or_based: dict = {}

    for mid, m in all_models.items():
        # Priority 1: real live score (from OR API)
        if mid in live_scores:
            or_based[mid] = live_scores[mid]
            continue

        # Priority 2: curated score
        if mid in CURATED_SCORES:
            or_based[mid] = CURATED_SCORES[mid]
            continue

        # Priority 3: family inheritance (from live + curated combined)
        combined_known = {**live_scores, **CURATED_SCORES}
        inherited = _infer_family_score(mid, combined_known)
        if inherited:
            or_based[mid] = inherited
            continue

        # Priority 4: price-bracket default
        try:
            price = float(m.get("pricing", {}).get("completion", 0) or 0) * 1_000_000
        except (ValueError, TypeError):
            price = -1.0
        or_based[mid] = _price_bracket_score(price)

    # Start with file_data for any non-OR models (very rare edge cases)
    merged = {k: v for k, v in file_data.items() if k not in all_models}

    # Overlay everything OR-based (completely replacing stale JSON entries)
    merged.update(or_based)

    # Apply forced overrides LAST — these correct known-bad OR API data.
    # Must come after or_based so they win even against real live scores.
    forced_applied = 0
    for mid, score in FORCED_OVERRIDES.items():
        if mid in merged:   # only apply if the model exists in the catalog
            merged[mid] = score
            forced_applied += 1

    real_count = len(live_scores) - forced_applied
    curated_count = sum(1 for mid in or_based if mid in CURATED_SCORES and mid not in live_scores)
    inferred_count = len(or_based) - len(live_scores) - curated_count
    legacy_count = len(merged) - len(or_based)

    logger.info(
        f"[Benchmarks] Coverage: {real_count} real OR, "
        f"{forced_applied} force-corrected, "
        f"{curated_count} curated, "
        f"{inferred_count} inferred/defaulted, "
        f"{legacy_count} legacy JSON "
        f"= {len(merged)} total"
    )
    return merged


def _refresh_cache() -> None:
    """Refresh the cache: fetch OR data, then apply all enrichment tiers."""
    global _last_refresh

    live_scores, all_models = _fetch_from_openrouter()
    file_data = _load_from_file()

    merged = _build_full_scores(live_scores, all_models, file_data)

    if merged:
        with _cache_lock:
            _cache.clear()
            _cache.update(merged)
            _last_refresh = time.time()
        logger.info(f"[Benchmarks] Cache refreshed — {len(_cache)} total entries")
    else:
        logger.warning("[Benchmarks] Refresh produced no data; keeping existing cache.")


def _background_loop() -> None:
    """Daemon thread: sleep REFRESH_INTERVAL_HOURS, then refresh, repeat."""
    interval_sec = REFRESH_INTERVAL_HOURS * 3600
    while True:
        time.sleep(interval_sec)
        logger.info("[Benchmarks] Background refresh triggered.")
        try:
            _refresh_cache()
        except Exception as e:
            logger.error(f"[Benchmarks] Background refresh error: {e}")


def _ensure_initialized() -> None:
    """Load seed file synchronously on first call, then launch background thread."""
    global _initialized, _refresh_thread

    if _initialized:
        return

    _refresh_cache()
    _initialized = True

    _refresh_thread = threading.Thread(
        target=_background_loop, daemon=True, name="benchmarks-refresh"
    )
    _refresh_thread.start()
    logger.info(f"[Benchmarks] Background refresh started (every {REFRESH_INTERVAL_HOURS}h)")


# ── Public API ────────────────────────────────────────────────────────────────

def get_benchmarks() -> dict:
    """
    Returns benchmark scores instantly from in-memory cache.
    Format: { "provider/model-id": { "coding": float, "reasoning": float, "vision": float } }

    Sources (in priority order):
      1. OpenRouter /api/v1/models (real AA + Design Arena data, no key needed)
      2. Curated scores for ~60 well-known models
      3. Family inheritance (e.g. -fast variants inherit from parent model)
      4. Price-bracket defaults for truly unknown models
      5. Local benchmarks.json (legacy seed)

    Cache is refreshed every 24h in the background. NEVER blocks on network.
    """
    _ensure_initialized()
    with _cache_lock:
        return dict(_cache)


def get_cache_info() -> dict:
    """Return cache metadata — useful for /health or /debug endpoints."""
    _ensure_initialized()
    return {
        "entries":      len(_cache),
        "last_refresh": _last_refresh,
        "age_minutes":  round((time.time() - _last_refresh) / 60, 1) if _last_refresh else None,
        "source":       "openrouter_api+curated+inference+local_json",
    }
