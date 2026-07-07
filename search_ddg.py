import json
from duckduckgo_search import DDGS

queries = [
    "site:reddit.com/r/JEENEETards \"2026\" doubt",
    "site:reddit.com/r/IndianAcademia \"2026\" doubt",
    "site:reddit.com/r/ApplyingToCollege \"2026\" help",
    "site:reddit.com/r/cbse \"2026\" doubt",
    "site:quora.com \"2026\" exam doubt"
]

all_results = []
try:
    with DDGS() as ddgs:
        for q in queries:
            print(f"Searching: {q}")
            results = ddgs.text(q, max_results=10)
            if results:
                for r in results:
                    all_results.append({
                        "title": r.get('title', ''),
                        "snippet": r.get('body', ''),
                        "url": r.get('href', ''),
                        "source": q.split(" ")[0]
                    })
except Exception as e:
    print("Error:", e)

with open("doubts.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=4)
print(f"Saved {len(all_results)} doubts.")
