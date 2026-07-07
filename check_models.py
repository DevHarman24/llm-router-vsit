import requests
resp = requests.get('https://openrouter.ai/api/v1/models', timeout=10)
data = resp.json().get('data', [])
targets = ['gpt-5', 'claude-opus-4', 'claude-sonnet-4', 'o3', 'o4']
found = [m for m in data if any(t in m.get('id','') for t in targets)]
for m in sorted(found, key=lambda x: x.get('id','')):
    pricing = m.get('pricing', {})
    price = float(pricing.get('completion', 0) or 0) * 1_000_000
    mid = m['id']
    print(mid + ' ' * max(1, 55-len(mid)) + 'price=' + str(round(price,3)) + '/M')
print('Total matching: ' + str(len(found)))
