"""
Dynamic Model Catalog
Fetches all available models from OpenRouter API and categorizes them into tiers
based on pricing, context window, and known capabilities.
"""

import requests
import json
import time
from dataclasses import dataclass, field
from typing import Optional
from functools import lru_cache
import os
from router.benchmarks import get_benchmarks

# --- CONFIG ---
USE_EPOCH_BENCHMARKS = True  # Toggle between True (Epoch ECI) and False (OpenRouter benchmarks.json)
# --------------

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Price thresholds per million output tokens (USD)
TIER1_MIN_PRICE = 5.0    # >= $5/M tokens → Tier 1 (most capable/expensive)
TIER2_MIN_PRICE = 0.5    # >= $0.5/M tokens → Tier 2 (mid-range)
# < $0.5/M tokens → Tier 3 (cheap/fast)

# Models known to have strong reasoning/thinking capability
# Note: only include true frontier/reasoning models here — being in this set
# forces Tier 1 assignment regardless of price, so keep it lean.
THINKING_MODELS = {
    # Anthropic
    "anthropic/claude-3-opus",
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-7-sonnet",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-opus-4",
    "anthropic/claude-fable-5",
    "anthropic/claude-fable-latest",
    # OpenAI
    "openai/o1",
    "openai/o3",
    "openai/o4-mini",
    "openai/gpt-5",
    "openai/gpt-5.5",
    "openai/gpt-5.5-pro",
    "openai/gpt-5.6-sol",
    "openai/gpt-5.6-terra",
    "openai/gpt-5.6-luna",
    # Google
    "google/gemini-2.0-flash-thinking-exp",
    "google/gemini-2.5-pro",
    "google/gemini-3",
    # DeepSeek
    "deepseek/deepseek-r1",
    # Qwen — thinking variants (mid/low tier)
    "qwen/qwq-32b",
    "qwen/qwen3-max-thinking",
    "qwen/qwen3-vl-8b-thinking",
    "qwen/qwen3-vl-30b-a3b-thinking",
    "qwen/qwen3-vl-235b-a22b-thinking",
    "qwen/qwen3-next-80b-a3b-thinking",
    "qwen/qwen-plus-2025-07-28:thinking",
    "qwen/qwen3-235b-a22b-thinking",
    "qwen/qwen3-30b-a3b-thinking",
    # AllenAI
    "allenai/olmo-3-32b-think",
    # Arcee
    "arcee-ai/trinity-large-thinking",
    # MoonShot
    "moonshotai/kimi-k2-thinking",
    # Sao10K (fine-tuned reasoning models)
    "sao10k/l3.3-euryale-70b",
    "sao10k/l3.1-euryale-70b",
    "sao10k/l3.1-70b-hanami-x1",
    "sao10k/l3-lunaris-8b",
}

# Models known for strong coding ability
CODING_MODELS = {
    # Anthropic
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-7-sonnet",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-opus-4",
    "anthropic/claude-fable-5",
    "anthropic/claude-fable-latest",
    # OpenAI
    "openai/gpt-4o",
    "openai/o3",
    "openai/o4-mini",
    "openai/gpt-5",
    "openai/gpt-5.5",
    "openai/gpt-5.5-pro",
    "openai/gpt-5.6-sol",
    "openai/gpt-5.6-terra",
    # DeepSeek
    "deepseek/deepseek-coder-v2",
    "deepseek/deepseek-r1",
    # Qwen
    "qwen/qwen-2.5-coder-32b-instruct",
    "qwen/qwen3-coder",
    # Mistral / Arcee coding specialists (mid tier)
    "mistralai/codestral",
    "mistralai/devstral",
    "arcee-ai/coder-large",
    # Kwaipilot / MoonShot code specialists
    "kwaipilot/kat-coder-pro",
    "moonshotai/kimi-k2.7-code",
    "moonshotai/kimi-k2-thinking",
    # Cohere
    "cohere/north-mini-code",
}

# Models that support vision/image input
VISION_MODELS = {
    # OpenAI
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-5",
    "openai/gpt-5.5",
    "openai/gpt-5.5-pro",
    "openai/gpt-5.6-sol",
    "openai/gpt-5.6-terra",
    "openai/gpt-5.6-luna",
    # Anthropic
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-7-sonnet",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-haiku",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-opus-4",
    "anthropic/claude-fable-5",
    "anthropic/claude-fable-latest",
    # Google
    "google/gemini-2.0-flash",
    "google/gemini-1.5-pro",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash-image",
    "google/gemini-3",
    # Meta
    "meta-llama/llama-3.2-90b-vision-instruct",
    "meta-llama/llama-3.2-11b-vision-instruct",
    # Qwen vision models (mid/low tier)
    "qwen/qwen2-vl-72b-instruct",
    "qwen/qwen2.5-vl-72b-instruct",
    "qwen/qwen3-vl-8b-instruct",
    "qwen/qwen3-vl-30b-a3b-instruct",
    "qwen/qwen3-vl-235b-a22b-instruct",
    "qwen/qwen3-vl-8b-thinking",
    "qwen/qwen3-vl-30b-a3b-thinking",
    "qwen/qwen3-vl-235b-a22b-thinking",
    "qwen/qwen3-vl-32b-instruct",
    # Nvidia
    "nvidia/nemotron-nano-12b-v2-vl",
    # Baidu
    "baidu/ernie-4.5-vl",
}


@dataclass
class ModelInfo:
    id: str
    name: str
    tier: int                     # 1=High, 2=Mid, 3=Low
    context_window: int
    price_per_million_tokens: float
    supports_vision: bool = False
    supports_thinking: bool = False
    supports_coding: bool = False
    provider: str = ""


def _extract_price(pricing: dict) -> float:
    """Extract the output price (per token) and convert to per-million."""
    try:
        completion_price = float(pricing.get("completion", 0) or 0)
        return completion_price * 1_000_000  # convert to per-million
    except (ValueError, TypeError):
        return 0.0


def _assign_tier(price_per_million: float, model_id: str, context_window: int) -> int:
    """Assign a tier based on pricing. Thinking models are boosted to Tier 1."""
    # Known thinking/frontier models always go to Tier 1
    if any(tm in model_id for tm in THINKING_MODELS):
        return 1
    if price_per_million >= TIER1_MIN_PRICE:
        return 1
    elif price_per_million >= TIER2_MIN_PRICE:
        return 2
    else:
        return 3


def fetch_model_catalog(timeout: int = 8) -> list[ModelInfo]:
    """
    Fetch all models from OpenRouter and return a sorted list of ModelInfo objects.
    Falls back to a small hardcoded list if the API is unreachable.
    """
    try:
        resp = requests.get(OPENROUTER_MODELS_URL, timeout=timeout)
        resp.raise_for_status()
        data = resp.json().get("data", [])

        models = []
        for m in data:
            model_id = m.get("id", "")
            name = m.get("name", model_id)
            context_window = int(m.get("context_length", 4096) or 4096)
            pricing = m.get("pricing", {})
            price = _extract_price(pricing)
            tier = _assign_tier(price, model_id, context_window)
            provider = model_id.split("/")[0] if "/" in model_id else "unknown"

            models.append(ModelInfo(
                id=model_id,
                name=name,
                tier=tier,
                context_window=context_window,
                price_per_million_tokens=price,
                supports_vision=any(vm in model_id for vm in VISION_MODELS),
                supports_thinking=any(tm in model_id for tm in THINKING_MODELS),
                supports_coding=any(cm in model_id for cm in CODING_MODELS),
                provider=provider,
            ))

        # Sort: tier ascending, then price ascending (cheapest capable model first within each tier)
        models.sort(key=lambda x: (x.tier, x.price_per_million_tokens))
        return models

    except Exception as e:
        print(f"[ModelCatalog] Warning: Could not fetch from OpenRouter ({e}). Using fallback list.")
        return _fallback_models()


def _fallback_models() -> list[ModelInfo]:
    """Hardcoded fallback in case OpenRouter is unreachable."""
    return [
        ModelInfo("openai/gpt-4o", "GPT-4o", 1, 128000, 15.0, True, False, True, "openai"),
        ModelInfo("anthropic/claude-3-5-sonnet", "Claude 3.5 Sonnet", 1, 200000, 15.0, True, True, True, "anthropic"),
        ModelInfo("google/gemini-2.5-pro", "Gemini 2.5 Pro", 1, 1000000, 10.0, True, True, False, "google"),
        ModelInfo("deepseek/deepseek-r1", "DeepSeek R1", 1, 128000, 8.0, False, True, True, "deepseek"),
        ModelInfo("openai/gpt-4o-mini", "GPT-4o Mini", 2, 128000, 0.6, True, False, False, "openai"),
        ModelInfo("anthropic/claude-3-haiku", "Claude 3 Haiku", 2, 200000, 1.25, True, False, False, "anthropic"),
        ModelInfo("google/gemini-2.0-flash", "Gemini 2.0 Flash", 2, 1000000, 0.7, True, False, False, "google"),
        ModelInfo("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B", 3, 131072, 0.06, False, False, False, "meta-llama"),
        ModelInfo("qwen/qwen-2.5-7b-instruct", "Qwen 2.5 7B", 3, 32768, 0.07, False, False, False, "qwen"),
        ModelInfo("deepseek/deepseek-chat", "DeepSeek V3", 3, 64000, 0.28, False, False, True, "deepseek"),
        ModelInfo("google/gemma-3-27b-it", "Gemma 3 27B", 3, 128000, 0.10, False, False, False, "google"),
    ]


# Singleton cache — loaded once per server startup
_catalog_cache: Optional[list[ModelInfo]] = None
_cache_timestamp: float = 0
CACHE_TTL_SECONDS = 3600  # Refresh every 1 hour

_epoch_benchmarks_cache = None

def get_epoch_benchmarks_data() -> dict:
    global _epoch_benchmarks_cache
    if _epoch_benchmarks_cache is None:
        try:
            path = os.path.join(os.path.dirname(__file__), "epoch_benchmarks.json")
            with open(path, "r", encoding="utf-8") as f:
                _epoch_benchmarks_cache = json.load(f)
        except Exception as e:
            print(f"[ModelCatalog] Failed to load epoch benchmarks: {e}")
            _epoch_benchmarks_cache = {}
    return _epoch_benchmarks_cache


def _fuzzy_match_epoch_score(model: ModelInfo, epoch_data: dict) -> float:
    # Try exact match first
    if model.name in epoch_data:
        return epoch_data[model.name].get("eci_score", 50.0)
        
    # Try fuzzy match (ignore case and some symbols)
    m_name = model.name.lower().replace("-", " ").replace(".", "")
    for k, v in epoch_data.items():
        k_name = k.lower().replace("-", " ").replace(".", "")
        if m_name in k_name or k_name in m_name:
            return v.get("eci_score", 50.0)
            
    # Default score if not found
    return 50.0


def get_catalog() -> list[ModelInfo]:
    global _catalog_cache, _cache_timestamp
    now = time.time()
    if _catalog_cache is None or (now - _cache_timestamp) > CACHE_TTL_SECONDS:
        _catalog_cache = fetch_model_catalog()
        _cache_timestamp = now
    return _catalog_cache


def get_best_model_for_tier(tier: int, needs_vision: bool = False,
                             needs_thinking: bool = False, needs_coding: bool = False,
                             min_context: int = 0, mode: str = "standard") -> Optional[ModelInfo]:
    """Return the best model for a given tier, filtered by capability requirements and mode."""
    catalog = get_catalog()
    candidates = [m for m in catalog if m.tier == tier]

    if needs_vision:
        vision_candidates = [m for m in candidates if m.supports_vision]
        if vision_candidates:
            candidates = vision_candidates

    if needs_thinking:
        thinking_candidates = [m for m in candidates if m.supports_thinking]
        if thinking_candidates:
            candidates = thinking_candidates

    if needs_coding:
        coding_candidates = [m for m in candidates if m.supports_coding]
        if coding_candidates:
            candidates = coding_candidates

    if min_context > 0:
        context_candidates = [m for m in candidates if m.context_window >= min_context]
        if context_candidates:
            candidates = context_candidates

    # Exclude free/meta-router models (price <= 0) — they are not real LLMs
    # and their zero/negative prices break cheap-mode scoring.
    # Also exclude insanely expensive models (> $200/M tokens) like o1-pro.
    # Keep unfiltered list as a fallback so we never return None unnecessarily.
    real_candidates = [m for m in candidates if 0 < m.price_per_million_tokens <= 200.0]
    if real_candidates:
        candidates = real_candidates

    if not candidates:
        return None

    # Score candidates based on mode
    def score_model(m: ModelInfo) -> float:
        # Lower score is better
        is_best_logic = (mode == "best") or (mode == "standard" and tier == 1)
        is_cheap_logic = (mode == "cheap")

        if is_cheap_logic:
            # Cheap logic: optimize purely for lowest cost
            return m.price_per_million_tokens
        elif is_best_logic:
            # Best logic: optimize for capability/benchmarks, but cost breaks ties among similar scores
            score = 0.0
            
            if USE_EPOCH_BENCHMARKS:
                epoch_data = get_epoch_benchmarks_data()
                eci_score = _fuzzy_match_epoch_score(m, epoch_data)
                # ECI scores are usually 0-200. Multiply by 100.
                score -= eci_score * 100
            else:
                benchmarks = get_benchmarks()
                model_scores = benchmarks.get(m.id, {"coding": 50, "reasoning": 50, "vision": 50})
                if needs_coding:
                    score -= model_scores.get("coding", 50) * 100
                elif needs_thinking:
                    score -= model_scores.get("reasoning", 50) * 100
                elif needs_vision:
                    score -= model_scores.get("vision", 50) * 100
                else:
                    score -= model_scores.get("reasoning", 50) * 50
                    
            # Context window bonus
            score -= (m.context_window / 1_000_000) * 10
            # Higher penalty for price so it becomes a factor when scores are almost the same.
            # E.g. $10 difference adds 100 to score (equivalent to 1 ECI point).
            score += (m.price_per_million_tokens * 10.0)
            return score
        else:
            # Standard logic: Balanced approach scoring price vs capabilities
            # We use task-specific benchmarks and provider bonuses to ensure a healthy mix.
            score = m.price_per_million_tokens * 10.0
            
            benchmarks = get_benchmarks()
            model_scores = benchmarks.get(m.id, {"coding": 50, "reasoning": 50, "vision": 50})
            
            # Apply task-specific bonuses to force a mix of providers based on their strengths
            if needs_coding:
                if m.provider in ["anthropic", "deepseek"]:
                    score -= 30.0  # Provider specialization bonus
                score -= model_scores.get("coding", 50) * 8.0
            elif needs_thinking:
                if m.provider in ["openai", "deepseek"]:
                    score -= 30.0
                score -= model_scores.get("reasoning", 50) * 8.0
            elif needs_vision:
                if m.provider in ["google", "openai"]:
                    score -= 30.0
                score -= model_scores.get("vision", 50) * 8.0
            else:
                score -= model_scores.get("reasoning", 50) * 5.0
            
            # Optionally blend in the general Epoch score, but at a lower weight so 
            # task-specific metrics and provider bonuses dictate the mix.
            if USE_EPOCH_BENCHMARKS:
                epoch_data = get_epoch_benchmarks_data()
                eci_score = _fuzzy_match_epoch_score(m, epoch_data)
                score -= eci_score * 5.0
            
            # Reward larger context windows slightly
            score -= (m.context_window / 100_000) * 0.5
            
            # Reward extra capabilities (nice to have)
            if m.supports_vision and not needs_vision:
                score -= 2.0
            if m.supports_thinking and not needs_thinking:
                score -= 5.0
            if m.supports_coding and not needs_coding:
                score -= 3.0
                
            return score

    # First sort alphabetically descending by ID (so e.g., 4.6 comes before 4.5).
    candidates.sort(key=lambda m: m.id, reverse=True)
    # Then sort by score (lower is better). Python's stable sort preserves the ID ordering for identical scores.
    candidates.sort(key=score_model)
    return candidates[0]

