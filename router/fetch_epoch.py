import json
import urllib.request
import csv
import io
import os
import logging

logging.basicConfig(level=logging.INFO, format="[Epoch Fetch] %(message)s")
logger = logging.getLogger(__name__)

ECI_CSV_URL = "https://epoch.ai/data/eci_scores.csv"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "epoch_benchmarks.json")

def fetch_and_convert():
    logger.info(f"Downloading Epoch Capabilities Index (ECI) dataset...")
    
    csv_data = None
    try:
        req = urllib.request.Request(ECI_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            csv_data = response.read().decode('utf-8')
            logger.info(f"Successfully downloaded from {ECI_CSV_URL}")
    except Exception as e:
        logger.error(f"Failed to download: {e}")
        return

    logger.info("Parsing CSV data...")
    reader = csv.DictReader(io.StringIO(csv_data))
    
    models = {}
    for row in reader:
        name = row.get("Display name", "").strip() or row.get("Model", "").strip()
        if not name:
            continue
            
        def get_val(key):
            v = row.get(key, "").strip()
            return None if v in ("", "NA", "NaN") else v

        try:
            eci_score = float(get_val("eci")) if get_val("eci") else None
        except:
            eci_score = None

        models[name] = {
            "organization": get_val("Organization"),
            "publication_date": get_val("date"),
            "eci_score": eci_score,
            "eci_ci_low": get_val("eci_ci_low"),
            "eci_ci_high": get_val("eci_ci_high"),
            "accessibility": get_val("Model accessibility")
        }

    logger.info(f"Successfully parsed {len(models)} ECI model scores.")
    
    # Sort models by ECI score descending before saving
    sorted_models = dict(sorted(models.items(), key=lambda item: item[1].get('eci_score') or 0, reverse=True))

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_models, f, indent=2)
        
    logger.info(f"Saved ECI benchmarks to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_and_convert()
