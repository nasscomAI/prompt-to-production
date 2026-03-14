import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    description = str(row.get('description', '')).lower()
    
    # Priority
    priority = "Standard"
    matched_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            matched_keyword = kw
            break
            
    # Check for categories
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "flooded": "Flooding",
        "water": "Flooding",
        "rain": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "lights": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "dump": "Waste",
        "animal": "Waste",
        "noise": "Noise",
        "loud": "Noise",
        "music": "Noise",
        "road": "Road Damage",
        "crack": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "block": "Drain Blockage"
    }
    
    matches = set()
    for k, v in category_map.items():
        if re.search(r'\b' + k + r'\b', description):
            matches.add(v)
            
    category = "Other"
    flag = ""
    
    if len(matches) == 1:
        category = list(matches)[0]
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # no match
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason length must be exactly one sentence and cite specific words.
    if priority == "Urgent":
        reason = f"The issue is classified with Urgent priority due to the word '{matched_keyword}' in the description."
    else:
        reason = f"The issue is structurally standard as it refers to general conditions."
        if len(matches) == 1:
            reason = f"The description contains category-specific words resolving it."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames) + ['category', 'priority', 'reason', 'flag']
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing row {row.get('id', 'unknown')}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
