"""
Router Engine — Main Orchestrator
Runs the dual-layer checkpoint system and returns routing decisions.
"""

import time
from dataclasses import dataclass
from typing import Optional

from router.heuristics import analyze as heuristic_analyze, HeuristicResult
from router.llm_classifier import classify as llm_classify, ClassifierResult
from router.models import get_best_model_for_tier, ModelInfo, get_catalog

# If heuristic confidence is >= this threshold, skip the LLM layer entirely
HEURISTIC_CONFIDENCE_THRESHOLD = 0.80


@dataclass
class RoutingDecision:
    model: ModelInfo
    tier: int
    tier_label: str
    heuristic: HeuristicResult
    classifier: Optional[ClassifierResult]
    total_time_ms: float
    heuristic_time_ms: float
    llm_time_ms: float
    llm_used: bool
    needs_vision: bool
    needs_thinking: bool
    needs_coding: bool
    signals: list[str]
    reasoning: str


TIER_LABELS = {1: "High Complexity", 2: "Medium Complexity", 3: "Low Complexity"}


def route(
    query: str,
    has_image: bool = False,
    has_file: bool = False,
    file_size_kb: float = 0,
    groq_api_key: Optional[str] = None,
    mode: str = "standard",
) -> RoutingDecision:
    """
    Main routing function. Returns a RoutingDecision with the recommended model.
    """
    overall_start = time.perf_counter()

    # ── LAYER A: Heuristics ─────────────────────────────────────────────────
    h_start = time.perf_counter()
    heuristic = heuristic_analyze(
        query=query,
        has_image=has_image,
        has_file=has_file,
        file_size_kb=file_size_kb
    )
    h_elapsed_ms = (time.perf_counter() - h_start) * 1000

    # ── LAYER B: LLM Classifier (only if heuristic is not confident enough) ──
    llm_used = False
    classifier: Optional[ClassifierResult] = None
    llm_elapsed_ms = 0.0

    if heuristic.confidence < HEURISTIC_CONFIDENCE_THRESHOLD:
        llm_start = time.perf_counter()
        classifier = llm_classify(query, heuristic, api_key=groq_api_key)
        llm_elapsed_ms = (time.perf_counter() - llm_start) * 1000
        llm_used = True

        # Use LLM classification result
        final_tier = classifier.tier
        needs_vision = classifier.needs_vision or has_image
        needs_thinking = classifier.needs_thinking
        needs_coding = classifier.needs_coding
        reasoning = classifier.reasoning
    else:
        # High confidence heuristic — skip LLM
        final_tier = heuristic.complexity
        needs_vision = heuristic.needs_vision
        needs_thinking = heuristic.needs_thinking
        needs_coding = heuristic.needs_coding
        reasoning = f"Heuristic confident ({heuristic.confidence:.0%}): {'; '.join(heuristic.signals[:2])}"

    # Calculate estimated tokens to find minimum context window
    # Rough estimate: 1 token per 4 characters of query
    estimated_tokens = len(query) // 4
    if has_file:
        estimated_tokens += int((file_size_kb * 1024) // 4)
    if has_image:
        estimated_tokens += 1000  # fixed buffer for image

    # Add a safety margin of 1000 tokens for system prompt + response
    min_context = estimated_tokens + 1000

    # ── MODEL SELECTION ────────────────────────────────────────────────────
    model = get_best_model_for_tier(
        tier=final_tier,
        needs_vision=needs_vision,
        needs_thinking=needs_thinking,
        needs_coding=needs_coding,
        min_context=min_context,
        mode=mode,
    )

    # Fallback: if no model found for tier, try adjacent tiers
    if not model:
        for fallback_tier in [1, 2, 3]:
            model = get_best_model_for_tier(
                tier=fallback_tier, 
                needs_vision=needs_vision,
                needs_thinking=needs_thinking,
                needs_coding=needs_coding,
                min_context=min_context,
                mode=mode,
            )
            if model:
                final_tier = fallback_tier
                break

    total_elapsed_ms = (time.perf_counter() - overall_start) * 1000

    return RoutingDecision(
        model=model,
        tier=final_tier,
        tier_label=TIER_LABELS.get(final_tier, "Unknown"),
        heuristic=heuristic,
        classifier=classifier,
        total_time_ms=total_elapsed_ms,
        heuristic_time_ms=h_elapsed_ms,
        llm_time_ms=llm_elapsed_ms,
        llm_used=llm_used,
        needs_vision=needs_vision,
        needs_thinking=needs_thinking,
        needs_coding=needs_coding,
        signals=heuristic.signals,
        reasoning=reasoning,
    )
