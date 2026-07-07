import json
with open('evaluation_best_results.json') as f:
    results = json.load(f)
for r in results:
    if 'sonnet' in r['model']:
        print(f"Q{r['id']}: {r['model']}")
        break
