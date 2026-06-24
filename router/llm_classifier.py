"""
LLM Classifier Layer
Uses Groq's llama-3.1-8b-instant as a fast, cheap "meta-router" to classify
queries that the heuristic layer is unsure about (confidence < threshold).
"""

import os
import json
import re
from dataclasses import dataclass
from typing import Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from router.heuristics import HeuristicResult

GROQ_MODEL = "llama-3.1-8b-instant"

ROUTER_SYSTEM_PROMPT = """You are an expert AI model router. Your job is to analyze user queries and classify them to help route them to the most appropriate LLM tier.

You must respond with ONLY a valid JSON object — no explanation, no markdown, no extra text.

Classify the query into:
- tier: 1 (high complexity), 2 (medium complexity), or 3 (low complexity)
- needs_thinking: true/false — requires deep reasoning, math, philosophy, strategy
- needs_coding: true/false — requires writing or debugging code, SVG, animations, scripts
- needs_vision: true/false — requires understanding or generating images

TIER GUIDE:
- Tier 1: Architecture design, complex algorithms, creative visual coding (SVG animations, 3D, shaders, particle systems, simulations), deep reasoning, legal/medical analysis, multi-step engineering, anything requiring expertise
- Tier 2: Writing emails/articles, basic explanations, general summaries, simple scripts, comparisons
- Tier 3: Factual lookups, greetings, simple translations, yes/no, definitions, basic formatting

IMPORTANT RULES:
- "make a SVG animation for solar system" looks short but is Tier 1 (complex animation + physics)
- "write a React app" is Tier 1 (full application)
- "what is Python" is Tier 3 (simple fact)
- "explain recursion" is Tier 2 (explanation, not deep reasoning)
- Any query involving animations, games, simulations, visual effects → Tier 1

Return ONLY this JSON:
{"tier": <1|2|3>, "needs_thinking": <true|false>, "needs_coding": <true|false>, "needs_vision": <true|false>, "reasoning": "<one sentence>"}"""


@dataclass
class ClassifierResult:
    tier: int
    needs_thinking: bool
    needs_coding: bool
    needs_vision: bool
    reasoning: str
    source: str  # "llm" or "mock"


def _parse_llm_response(text: str) -> Optional[dict]:
    """Extract JSON from LLM response robustly."""
    text = text.strip()
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting JSON block
    match = re.search(r'\{[^}]+\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _mock_classify(query: str, heuristic: HeuristicResult) -> ClassifierResult:
    """
    Fallback mock classifier used when Groq API key is not set.
    Simply upgrades the heuristic result when confidence is low.
    """
    tier = heuristic.complexity
    # When confidence is borderline, default to one tier higher (safer)
    if heuristic.confidence < 0.6 and tier < 1:
        tier = max(1, tier - 1)

    return ClassifierResult(
        tier=tier,
        needs_thinking=heuristic.needs_thinking,
        needs_coding=heuristic.needs_coding,
        needs_vision=heuristic.needs_vision,
        reasoning="(Mock classifier — add GROQ_API_KEY to enable LLM classification)",
        source="mock"
    )


def classify(query: str, heuristic: HeuristicResult,
             api_key: Optional[str] = None) -> ClassifierResult:
    """
    Call Groq's llama-3.1-8b-instant to classify the query complexity.
    Falls back to mock if API key is unavailable.
    """
    key = api_key or os.getenv("GROQ_API_KEY", "")

    if not key or not GROQ_AVAILABLE:
        return _mock_classify(query, heuristic)

    try:
        client = Groq(api_key=key)

        # Build context for the LLM
        context = f"Query: {query}"
        if heuristic.needs_vision:
            context += "\n[User attached an image]"

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.1,  # Low temperature for consistent routing
            max_tokens=150,
        )

        raw = response.choices[0].message.content or ""
        parsed = _parse_llm_response(raw)

        if not parsed:
            return _mock_classify(query, heuristic)

        tier = int(parsed.get("tier", heuristic.complexity))
        tier = max(1, min(3, tier))  # Clamp to 1-3

        return ClassifierResult(
            tier=tier,
            needs_thinking=bool(parsed.get("needs_thinking", heuristic.needs_thinking)),
            needs_coding=bool(parsed.get("needs_coding", heuristic.needs_coding)),
            needs_vision=bool(parsed.get("needs_vision", heuristic.needs_vision)),
            reasoning=parsed.get("reasoning", ""),
            source="llm"
        )

    except Exception as e:
        print(f"[LLMClassifier] Groq API error: {e}. Falling back to mock.")
        return _mock_classify(query, heuristic)
