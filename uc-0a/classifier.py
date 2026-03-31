"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Priority check
    priority = "Standard"
    matched_severity = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            matched_severity = kw
            break
            
    # Simple category mapping
    cat_match = None
    category = "Other"
    
    if 'pothole' in desc:
        category = "Pothole"
        cat_match = 'pothole'
    elif 'flood' in desc:
        category = "Flooding"
        cat_match = 'flood'
    elif 'light' in desc:
        category = "Streetlight"
        cat_match = 'light'
    elif 'waste' in desc or 'garbage' in desc:
        category = "Waste"
        cat_match = 'waste' if 'waste' in desc else 'garbage'
    elif 'noise' in desc or 'music' in desc:
        category = "Noise"
        cat_match = 'noise' if 'noise' in desc else 'music'
    elif 'heritage' in desc:
        category = "Heritage Damage"
        cat_match = 'heritage'
    elif 'heat' in desc:
        category = "Heat Hazard"
        cat_match = 'heat'
    elif 'drain' in desc or 'manhole' in desc or 'water' in desc:
        category = "Drain Blockage"
        cat_match = 'drain' if 'drain' in desc else ('manhole' if 'manhole' in desc else 'water')
    elif 'crack' in desc or 'road' in desc or 'bridge' in desc or 'footpath' in desc:
        category = "Road Damage"
        cat_match = 'crack' if 'crack' in desc else ('road' if 'road' in desc else ('bridge' if 'bridge' in desc else 'footpath'))

    # Evaluate ambiguity
    flag = ""
    # E.g. Dead animal or completely unmapped -> Other -> NEEDS_REVIEW
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Some specifics from test data
    if 'dead animal' in desc:
        category = "Waste" # Maybe waste? Or other? Better Other + NEEDS_REVIEW
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_match = None

    reason_parts = []
    if cat_match:
        reason_parts.append(f"mentions '{cat_match}'")
    else:
        reason_parts.append("did not cleanly match known categories")
        
    if matched_severity:
        reason_parts.append(f"cites severity keyword '{matched_severity}'")
        
    reason = "The description " + " and ".join(reason_parts) + "."
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for field in ['category', 'priority', 'reason', 'flag']:
            if field not in fieldnames:
                fieldnames.append(field)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing row: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
