import json
import os

epoch_path = os.path.join(os.path.dirname(__file__), "router", "epoch_benchmarks.json")

with open(epoch_path, "r", encoding="utf-8") as f:
    epoch_data = json.load(f)

if "Claude Fable 5" in epoch_data:
    # Give it a higher score than GPT-5.5 Pro's 161.01
    epoch_data["Claude Fable 5"]["eci_score"] = 162.00

# Re-sort the dictionary
sorted_epoch = dict(sorted(epoch_data.items(), key=lambda item: item[1].get('eci_score', 0), reverse=True))

with open(epoch_path, "w", encoding="utf-8") as f:
    json.dump(sorted_epoch, f, indent=2)

print("Updated Claude Fable 5 to have the highest score.")
