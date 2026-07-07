import sys, os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, '.')
import router.benchmarks as bm

print('Fetching benchmarks... This will call AA API since the key is set.')
scores = bm.get_benchmarks()
info = bm.get_cache_info()

print('\n=== CACHE INFO ===')
for k, v in info.items():
    print(f'{k}: {v}')

print('\n=== REAL SCORES FETCHED ===')
kimi = 'moonshotai/kimi-k2.6'
gpt4o = 'openai/gpt-4o-2024-05-13'

if kimi in scores:
    print(f'Kimi K2.6: {scores[kimi]}')
else:
    print('Kimi K2.6 not found in merged scores.')

if gpt4o in scores:
    print(f'GPT-4o: {scores[gpt4o]}')
else:
    print('GPT-4o not found in merged scores.')

