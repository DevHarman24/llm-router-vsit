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

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Price thresholds per million output tokens (USD)
TIER1_MIN_PRICE = 5.0    # >= $5/M tokens → Tier 1 (most capable/expensive)
TIER2_MIN_PRICE = 0.5    # >= $0.5/M tokens → Tier 2 (mid-range)
# < $0.5/M tokens → Tier 3 (cheap/fast)

# Models known to have strong reasoning/thinking capability
# Note: only include true frontier/reasoning models here — being in this set
# forces Tier 1 assignment regardless of price, so keep it lean.
THINKING_MODELS = {
    "anthropic/claude-3-opus",
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-7-sonnet",
    "openai/o1",
    "openai/o3",
    "google/gemini-2.0-flash-thinking-exp",
    "google/gemini-2.5-pro",
    "deepseek/deepseek-r1",
    "qwen/qwq-32b",
}

# Models known for strong coding ability
CODING_MODELS = {
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-7-sonnet",
    "openai/gpt-4o",
    "openai/o4-mini",
    "deepseek/deepseek-coder-v2",
    "deepseek/deepseek-r1",
    "qwen/qwen-2.5-coder-32b-instruct",
}

# Models that support vision/image input
VISION_MODELS = {
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-7-sonnet",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-haiku",
    "google/gemini-2.0-flash",
    "google/gemini-1.5-pro",
    "google/gemini-2.5-pro",
    "meta-llama/llama-3.2-90b-vision-instruct",
    "meta-llama/llama-3.2-11b-vision-instruct",
    "qwen/qwen2-vl-72b-instruct",
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


def get_catalog() -> list[ModelInfo]:
    global _catalog_cache, _cache_timestamp
    now = time.time()
    if _catalog_cache is None or (now - _cache_timestamp) > CACHE_TTL_SECONDS:
        _catalog_cache = fetch_model_catalog()
        _cache_timestamp = now
    return _catalog_cache


def get_best_model_for_tier(tier: int, needs_vision: bool = False,
                             needs_thinking: bool = False, needs_coding: bool = False,
                             min_context: int = 0) -> Optional[ModelInfo]:
    """Return the best model for a given tier, filtered by capability requirements."""
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

    if not candidates:
        return None

    # Score candidates to avoid always picking the cheapest
    # Lower score is better
    def score_model(m: ModelInfo) -> float:
        score = m.price_per_million_tokens
        
        # Reward larger context windows slightly
        score -= (m.context_window / 100_000) * 0.05
        
        # Reward extra capabilities (nice to have)
        if m.supports_vision and not needs_vision:
            score -= 0.02
        if m.supports_thinking and not needs_thinking:
            score -= 0.1
        if m.supports_coding and not needs_coding:
            score -= 0.05
            
        return score

    candidates.sort(key=score_model)
    return candidates[0]
