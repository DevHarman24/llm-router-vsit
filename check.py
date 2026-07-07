import requests
data = requests.get("https://openrouter.ai/api/v1/models").json().get("data", [])
for m in data:
    if "claude-sonnet-4.5" in m["id"] or "claude-sonnet-4.6" in m["id"]:
        print(f"{m['id']}: context={m.get('context_length')}, price={m.get('pricing', {}).get('completion')}")
