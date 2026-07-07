import sys, os
sys.path.insert(0, '.')
from router.engine import route

QUERIES = [
    ('simple',  'What is 2 + 2?'),
    ('coding',  'Write a Python function to merge two sorted linked lists.'),
    ('complex', 'Explain the philosophical implications of Godels incompleteness theorems.'),
]
MODES = ['cheap', 'standard', 'best']

for mode in MODES:
    print(f'\n{"="*60}')
    print(f'  MODE: {mode.upper()}')
    print(f'{"="*60}')
    for label, query in QUERIES:
        print(f'\n  [{label.upper()}] {query[:58]}')
        try:
            d = route(query=query, mode=mode)
            m = d.model
            print(f'    Model : {m.name} ({m.id})')
            print(f'    Tier  : {d.tier} | {d.tier_label}')
            print(f'    Price : {m.price_per_million_tokens:.3f}/M tokens')
            print(f'    LLM   : {d.llm_used}  Time: {d.total_time_ms:.1f}ms')
        except Exception as e:
            print(f'    ERROR: {e}')
print('\nDone.')
