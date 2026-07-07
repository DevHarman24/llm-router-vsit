from router.models import get_catalog, get_best_model_for_tier
from router.benchmarks import get_benchmarks

catalog = get_catalog()
benchmarks = get_benchmarks()

candidates = [m for m in catalog if m.tier == 1]
thinking_candidates = [m for m in candidates if m.supports_thinking]
real_candidates = [m for m in thinking_candidates if 0 < m.price_per_million_tokens <= 1000.0]

for m in real_candidates:
    model_scores = benchmarks.get(m.id, {'coding': 50, 'reasoning': 50, 'vision': 50})
    score = 0.0
    score -= model_scores.get('reasoning', 50) * 100
    score -= (m.context_window / 1000000) * 10
    score -= m.price_per_million_tokens
    
    if 'opus-4.8' in m.id or 'o1-pro' in m.id or 'o3' in m.id:
        print(f"{m.id}: reasoning={model_scores.get('reasoning', 50)} price={m.price_per_million_tokens} score={score}")
