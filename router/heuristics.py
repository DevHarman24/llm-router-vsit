"""
Heuristics Layer — Traditional Coding Checkpoint
Fast, zero-cost complexity analysis of a query using rules, regex, and linguistic signals.
Returns a complexity score (1-3) and detected capabilities needed.
"""

import re
from dataclasses import dataclass, field


@dataclass
class HeuristicResult:
    complexity: int              # 1=High, 2=Medium, 3=Low (maps to tier)
    confidence: float            # 0.0 to 1.0 — how confident the heuristic is
    needs_vision: bool = False
    needs_thinking: bool = False
    needs_coding: bool = False
    signals: list[str] = field(default_factory=list)  # Debug: which rules fired


# ─────────────────────────────────────────────
# HIGH COMPLEXITY SIGNALS (Tier 1)
# ─────────────────────────────────────────────
HIGH_COMPLEXITY_KEYWORDS = [
    # Deep reasoning / analysis
    r"\barchitect\b", r"\bdesign system\b", r"\bsystem design\b",
    r"\brefactor\b", r"\boptimize\b", r"\bperformance tuning\b",
    r"\bcomplex algorithm\b", r"\badvanced\b.*\balgorithm\b",
    r"\bproof\b.*\bmath\b", r"\btheorem\b", r"\bderive\b",
    r"\bdeep learning\b", r"\bmachine learning model\b", r"\btrain\b.*\bmodel\b",
    r"\bnlp pipeline\b", r"\btransformer\b.*\bscratch\b",
    r"\bfull[\s-]stack\b", r"\bmicroservices\b", r"\bkubernetes\b", r"\borchestrate\b",
    r"\bsecurity audit\b", r"\bpenetration test\b", r"\bvulnerability\b",
    r"\bbusiness strategy\b", r"\bcompetitive analysis\b",
    r"\blegal document\b", r"\bcontract review\b",
    # Deceptively complex creative/visual tasks
    r"\bsvg\b.*\banimation\b", r"\banimated\b.*\bsvg\b",
    r"\bsolar system\b", r"\b3d\b.*\banimation\b", r"\bparticle system\b",
    r"\bshader\b", r"\bwebgl\b", r"\bthree\.?js\b",
    r"\bphysics simulation\b", r"\bcollision detection\b",
    r"\bprocedural generation\b", r"\bgenerative art\b",
    # Long multi-step instructions
    r"\bstep[\s-]by[\s-]step\b.*\b(build|create|implement|design)\b",
    r"\bend[\s-]to[\s-]end\b", r"\bcomplete\b.*\bapplication\b",
    r"\bfrom scratch\b",
]

# ─────────────────────────────────────────────
# CODING SIGNALS (code-capable model needed)
# ─────────────────────────────────────────────
CODING_SIGNALS = [
    r"\b(code|coding|program|script|function|class|method|api|bug|debug|error|fix|implement|build)\b",
    r"```", r"\bdef \b", r"\bclass \b", r"\bimport \b", r"\breturn \b",
    r"\bjavascript\b", r"\bpython\b", r"\brust\b", r"\bgo\b", r"\bswift\b",
    r"\btypescript\b", r"\breact\b", r"\bnext\.?js\b", r"\bnode\.?js\b",
    r"\bsql\b", r"\bdatabase\b", r"\bquery\b",
    r"\bsvg\b", r"\bcss animation\b", r"\bhtml\b.*\bcanvas\b",
]

# ─────────────────────────────────────────────
# THINKING SIGNALS (reasoning-heavy model needed)
# ─────────────────────────────────────────────
THINKING_SIGNALS = [
    r"\bwhy\b.*\b(is|does|should|would|could)\b",
    r"\bexplain\b.*\b(how|why|what)\b",
    r"\banalyze\b", r"\banalyse\b", r"\breason\b", r"\bthink through\b",
    r"\bpros\b.*\bcons\b", r"\btrade.?off\b", r"\bcompare\b.*\bcontrast\b",
    r"\bphilosoph\b", r"\bethics\b", r"\bmoral\b",
    r"\bmath\b", r"\bcalculate\b", r"\bsolve\b.*\bequation\b",
    r"\bprove\b", r"\bproof\b",
    r"\bdecision\b.*\bframework\b", r"\bstrategic\b",
]

# ─────────────────────────────────────────────
# MEDIUM COMPLEXITY SIGNALS (Tier 2)
# ─────────────────────────────────────────────
MEDIUM_COMPLEXITY_KEYWORDS = [
    r"\bwrite\b.*\b(email|report|blog|article|essay|letter)\b",
    r"\bsummariz\b.*\b(long|detailed|document|report)\b",
    r"\bexplain\b", r"\bdescribe\b", r"\bcompare\b",
    r"\bplan\b", r"\boutline\b", r"\bbrainstorm\b",
    r"\breview\b", r"\bfeedback\b",
    r"\btranslate\b.*\b(paragraph|document|article)\b",
    r"\bsimple\b.*\bscript\b", r"\bbasic\b.*\bcode\b",
]

# ─────────────────────────────────────────────
# LOW COMPLEXITY SIGNALS (Tier 3)
# ─────────────────────────────────────────────
LOW_COMPLEXITY_KEYWORDS = [
    # These patterns only match SHORT, clearly factual questions.
    # e.g. "What is water?" matches, but "What is the difference between a philosophical zombie..." does NOT.
    r"^what is \w+\??$",       # Only if query is literally "What is X?"
    r"^who is \w+\??$",        # e.g. "Who is Einstein?"
    r"^when is \w+\??$",       # e.g. "When is Christmas?"
    r"^where is \w+\??$",      # e.g. "Where is Paris?"
    r"\bhello\b", r"\bhi\b", r"\bhey\b",
    r"\bthank\b", r"\bthanks\b",
    r"\btranslate\b.*\bword\b", r"\bdefine\b", r"\bsynonym\b", r"\bantonym\b",
    r"\bcapital of\b", r"\bwhat.*weather\b",
    r"\bjoke\b", r"\bfun fact\b",
    r"\bformat\b.*\b(list|table|json|csv)\b",
    r"\byes or no\b", r"\btrue or false\b",
    # Note: "find", "search", "extract" intentionally removed — they appear in
    # complex coding/analysis queries and were causing false low-complexity matches.
]


def _match_patterns(text: str, patterns: list[str]) -> list[str]:
    """Return list of pattern labels that matched the text."""
    matched = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(pattern)
    return matched


def analyze(query: str, has_image: bool = False, has_file: bool = False,
            file_size_kb: float = 0) -> HeuristicResult:
    """
    Run all heuristic checks on a query and return a structured result.
    """
    signals = []
    needs_vision = has_image
    needs_thinking = False
    needs_coding = False

    text = query.strip()
    word_count = len(text.split())
    char_count = len(text)

    # ── Vision detection ──────────────────────────────
    if has_image:
        signals.append("has_image → needs_vision")

    # ── Coding detection ─────────────────────────────
    coding_matches = _match_patterns(text, CODING_SIGNALS)
    if coding_matches:
        needs_coding = True
        signals.append(f"coding_signals({len(coding_matches)} matches)")

    # ── Thinking detection ───────────────────────────
    thinking_matches = _match_patterns(text, THINKING_SIGNALS)
    if thinking_matches:
        needs_thinking = True
        signals.append(f"thinking_signals({len(thinking_matches)} matches)")

    # ── High complexity signals ───────────────────────
    high_matches = _match_patterns(text, HIGH_COMPLEXITY_KEYWORDS)
    if high_matches:
        signals.append(f"high_complexity_keywords({len(high_matches)} matches): {high_matches[:2]}")
        return HeuristicResult(
            complexity=1, confidence=0.90,
            needs_vision=needs_vision, needs_thinking=True,
            needs_coding=needs_coding or any("svg" in m or "code" in m or "script" in m for m in high_matches),
            signals=signals
        )

    # Length alone doesn't mean high complexity, but we can note it
    if word_count > 150 or (has_file and file_size_kb > 50):
        signals.append(f"long_query(words={word_count}, file_kb={file_size_kb:.1f})")

    # ── Medium complexity ─────────────────────────────
    medium_matches = _match_patterns(text, MEDIUM_COMPLEXITY_KEYWORDS)
    if medium_matches:
        signals.append(f"medium_complexity_keywords({len(medium_matches)} matches)")
        # Coding + medium → bump to Tier 1
        if needs_coding and word_count > 30:
            signals.append("coding+medium+long → bump to Tier 1")
            return HeuristicResult(
                complexity=1, confidence=0.65,
                needs_vision=needs_vision, needs_thinking=needs_thinking,
                needs_coding=needs_coding, signals=signals
            )
        return HeuristicResult(
            complexity=2, confidence=0.75,
            needs_vision=needs_vision, needs_thinking=needs_thinking,
            needs_coding=needs_coding, signals=signals
        )

    # ── Low complexity ────────────────────────────────
    low_matches = _match_patterns(text, LOW_COMPLEXITY_KEYWORDS)
    if low_matches:
        signals.append(f"low_complexity_keywords({len(low_matches)} matches)")
        # IMPORTANT: if coding or thinking signals were already detected,
        # do NOT blindly override them with low complexity.
        # Instead, give it low confidence so the LLM classifier can decide.
        if needs_coding or needs_thinking:
            signals.append("low_keyword_overridden_by_coding_or_thinking")
            return HeuristicResult(
                complexity=2, confidence=0.35,
                needs_vision=needs_vision, needs_thinking=needs_thinking,
                needs_coding=needs_coding, signals=signals
            )
        return HeuristicResult(
            complexity=3, confidence=0.90,
            needs_vision=needs_vision, needs_thinking=False,
            needs_coding=False, signals=signals
        )

    # ── Fallback: short = low, medium = mid, long = high ──
    if word_count <= 8:
        signals.append(f"short_query(words={word_count})")
        return HeuristicResult(
            complexity=3, confidence=0.50,
            needs_vision=needs_vision, needs_thinking=needs_thinking,
            needs_coding=needs_coding, signals=signals
        )
    elif word_count <= 40:
        signals.append(f"medium_length_query(words={word_count})")
        # If it has coding or thinking signals, push to Tier 1
        if needs_coding or needs_thinking:
            return HeuristicResult(
                complexity=1, confidence=0.55,
                needs_vision=needs_vision, needs_thinking=needs_thinking,
                needs_coding=needs_coding, signals=signals
            )
        return HeuristicResult(
            complexity=2, confidence=0.45,
            needs_vision=needs_vision, needs_thinking=needs_thinking,
            needs_coding=needs_coding, signals=signals
        )
    else:
        signals.append(f"long_query_fallback(words={word_count})")
        # Just because it's long doesn't mean it's highly complex.
        # Give it Tier 2 with low confidence so the LLM classifier can re-evaluate.
        return HeuristicResult(
            complexity=2, confidence=0.45,
            needs_vision=needs_vision, needs_thinking=needs_thinking,
            needs_coding=needs_coding, signals=signals
        )
