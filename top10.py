import json
import os
from router.benchmarks import get_benchmarks

print("=== TOP 10 MODELS: EPOCH (ECI SCORE) ===")
epoch_path = os.path.join("router", "epoch_benchmarks.json")
with open(epoch_path, "r", encoding="utf-8") as f:
    epoch_data = json.load(f)

# epoch_data is already sorted when saved, but let's be sure
sorted_epoch = sorted(epoch_data.items(), key=lambda x: x[1].get("eci_score", 0) or 0, reverse=True)
for i, (name, stats) in enumerate(sorted_epoch[:10]):
    score = stats.get("eci_score")
    print(f"{i+1}. {name}: {score:.2f} ECI")

print("\n=== TOP 10 MODELS: OPENROUTER (REASONING/CODING/VISION) ===")
# Use get_benchmarks() which computes the full enriched OpenRouter catalog
or_data = get_benchmarks()

# Let's sort by the average of the 3 scores (coding, reasoning, vision)
def avg_score(scores):
    return (scores.get("coding", 0) + scores.get("reasoning", 0) + scores.get("vision", 0)) / 3.0

sorted_or = sorted(or_data.items(), key=lambda x: avg_score(x[1]), reverse=True)
for i, (model_id, stats) in enumerate(sorted_or[:10]):
    c = stats.get("coding", 0)
    r = stats.get("reasoning", 0)
    v = stats.get("vision", 0)
    avg = avg_score(stats)
    print(f"{i+1}. {model_id}: {avg:.1f} avg (Coding: {c}, Reasoning: {r}, Vision: {v})")
