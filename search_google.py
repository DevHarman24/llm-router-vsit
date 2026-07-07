from googlesearch import search
import json

queries = [
    "site:reddit.com/r/JEENEETards \"2026\" doubt",
    "site:reddit.com/r/IndianAcademia \"2026\" doubt",
    "site:quora.com \"2026\" (boards OR neet OR jee) doubt",
    "site:reddit.com/r/cbse \"2026\" doubt",
]

all_results = []
try:
    for q in queries:
        print(f"Searching: {q}")
        results = search(q, num_results=10, advanced=True)
        for r in results:
            all_results.append({
                "title": r.title,
                "snippet": r.description,
                "url": r.url,
                "source": q.split(" ")[0]
            })
except Exception as e:
    print("Error:", e)

with open("doubts.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=4)
print(f"Saved {len(all_results)} doubts.")
