import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = [
    "https://www.reddit.com/r/JEENEETards/search.json?q=2026+doubt&restrict_sr=on&sort=new&limit=20",
    "https://www.reddit.com/r/cbse/search.json?q=2026+doubt&restrict_sr=on&sort=new&limit=10",
    "https://www.reddit.com/r/IndianAcademia/search.json?q=2026+help&restrict_sr=on&sort=new&limit=10",
    "https://www.reddit.com/r/ApplyingToCollege/search.json?q=2026+help&restrict_sr=on&sort=new&limit=10"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
results = []

for q in queries:
    try:
        req = urllib.request.Request(q, headers=headers)
        response = urllib.request.urlopen(req, context=ctx)
        data = json.loads(response.read().decode())
        for child in data['data']['children']:
            title = child['data']['title']
            url = "https://www.reddit.com" + child['data']['permalink']
            subreddit = child['data']['subreddit']
            results.append({"title": title, "url": url, "subreddit": subreddit})
    except Exception as e:
        print(f"Error fetching {q}: {e}")

with open("doubts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)
print(f"Saved {len(results)} doubts.")
