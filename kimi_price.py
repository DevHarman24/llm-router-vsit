import requests
resp = requests.get('https://openrouter.ai/api/v1/models', timeout=10)
data = resp.json().get('data', [])
for m in data:
    if 'kimi' in m.get('id','').lower():
        mid = m['id']
        pricing = m.get('pricing', {})
        prompt = float(pricing.get('prompt', 0) or 0) * 1_000_000
        completion = float(pricing.get('completion', 0) or 0) * 1_000_000
        print(mid + '  prompt=' + str(round(prompt,3)) + '/M  completion=' + str(round(completion,3)) + '/M')
