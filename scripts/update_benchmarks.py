import json
import os
import requests
import time

# Paths
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)
BENCHMARKS_FILE = os.path.join(ROOT_DIR, "router", "benchmarks.json")

# You can add APIs for leaderboards here when they become available.
# For now, we will use OpenRouter API to fetch all active models and assign baseline scores
# based on known heuristics, updating the local cache seamlessly.
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

def fetch_openrouter_catalog():
    print("Fetching live model catalog from OpenRouter...")
    response = requests.get(OPENROUTER_MODELS_URL)
    response.raise_for_status()
    return response.json().get("data", [])

def fetch_live_benchmarks():
    """
    In the future, you can integrate with HuggingFace, LMSYS Arena API, or Aider's GitHub repo here.
    For this MVP, we build dynamic baseline scores based on the current OpenRouter catalog.
    """
    models = fetch_openrouter_catalog()
    live_scores = {}
    
    print(f"Processing {len(models)} models...")
    
    for m in models:
        model_id = m.get("id", "")
        # Fallback default scores
        coding = 50
        reasoning = 50
        vision = 50
        
        # Determine capabilities and base scores from pricing & context
        # Higher price / context usually correlates with capability
        pricing = m.get("pricing", {})
        try:
            price_per_m = float(pricing.get("completion", 0)) * 1_000_000
        except:
            price_per_m = 0
            
        context = int(m.get("context_length", 4096) or 4096)
        
        # Boost based on price/context proxy
        bonus = min(20, int(price_per_m) + int(context / 100000))
        
        coding += bonus
        reasoning += bonus
        vision += bonus
        
        # Apply strict bonuses for known frontier model families based on community consensus
        model_name = model_id.lower()
        if "opus" in model_name:
            coding += 45
            reasoning += 45
            vision += 45
        elif "sonnet" in model_name:
            coding += 30
            reasoning += 25
            vision += 25
        elif "o1" in model_name or "o3" in model_name or "r1" in model_name:
            reasoning += 35
            coding += 25
        elif "gpt-4o" in model_name or "gemini-2.5-pro" in model_name:
            vision += 30
            reasoning += 25
            coding += 20
        elif "llama" in model_name or "qwen" in model_name:
            coding -= 5  # adjust mid-tier baselines
            
        # Cap at 100
        live_scores[model_id] = {
            "coding": min(100, coding),
            "reasoning": min(100, reasoning),
            "vision": min(100, vision)
        }
        
    return live_scores

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def update_benchmarks_file():
    print(f"Updating {BENCHMARKS_FILE}...")
    try:
        new_scores = fetch_live_benchmarks()
        
        # Write heuristically generated scores atomically first so that
        # _fetch_from_aa() can read the full list of local keys.
        temp_file = BENCHMARKS_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(new_scores, f, indent=2)
            
        os.replace(temp_file, BENCHMARKS_FILE)
        
        # Fetch live benchmarks from Artificial Analysis
        from router.benchmarks import _fetch_from_aa
        print("Fetching live scores from Artificial Analysis API...")
        aa_scores = _fetch_from_aa()
        
        if aa_scores:
            print(f"Merging {len(aa_scores)} live scores from AA API...")
            new_scores.update(aa_scores)
            
            # Rewrite with merged scores
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(new_scores, f, indent=2)
            os.replace(temp_file, BENCHMARKS_FILE)
            print("Benchmarks successfully updated with live API data!")
        else:
            print("Benchmarks successfully updated (heuristic only, no live API data returned).")
            
    except Exception as e:
        print(f"Failed to update benchmarks: {e}")

if __name__ == "__main__":
    update_benchmarks_file()
