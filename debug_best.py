import sys
sys.path.insert(0, '.')
from router.models import get_catalog, get_best_model_for_tier
from router.benchmarks import get_benchmarks

benchmarks = get_benchmarks()
catalog = get_catalog()

# Show all tier-1 coding-capable models and their scores
print('=== TIER 1 MODELS (coding capable) ===')
tier1 = [m for m in catalog if m.tier == 1 and m.supports_coding]
tier1.sort(key=lambda m: m.price_per_million_tokens)
for m in tier1:
    bm = benchmarks.get(m.id, {})
    coding_score = bm.get('coding', 50)
    print(m.id[:50].ljust(52) + ' coding=' + str(coding_score) + '  price=' + str(round(m.price_per_million_tokens,2)) + '/M')

print()
print('=== BEST mode picks for coding: ===')
winner = get_best_model_for_tier(tier=1, needs_coding=True, mode='best')
print('Winner:', winner.id if winner else 'None')

# Also show gpt-5.5 and claude-opus-4.8 in catalog at all
print()
print('=== gpt-5.5 / claude-opus-4 in catalog? ===')
for m in catalog:
    if 'gpt-5.5' in m.id or 'claude-opus-4.8' in m.id or 'claude-opus-4.7' in m.id:
        print(m.id.ljust(52) + ' tier=' + str(m.tier) + ' coding=' + str(m.supports_coding) + ' price=' + str(round(m.price_per_million_tokens,2)))
