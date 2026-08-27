"""
UC-0A — Complaint Classifier
Implementation based on agents.md + skills.md strict RICE constraints.
"""
import argparse
import csv
import sys

# Fixed exact strings directly pulled from the RICE enforcement schema
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Robust word mappings derived from sample and schema bounds
CATEGORY_MAPPINGS = {
    "Pothole": ["pothole", "crater", "hole"],
    "Flooding": ["flood", "waterlogging", "submerged", "overflow"],
    "Streetlight": ["streetlight", "dark", "no light", "sparking"],
    "Waste": ["garbage", "trash", "waste", "rubbish", "smell", "dump"],
    "Noise": ["noise", "loud", "music", "party"],
    "Road Damage": ["crack", "road surface", "broken road", "broken", "upturned"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "sun", "temperature"],
    "Drain Blockage": ["drain", "clog", "blockage"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based purely on text matching.
    Returns: dict with populated keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority Enforcement
    is_urgent = any(kw in desc for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Category enforcement logic
    matched_cats = []
    reason_kw = None
    
    for cat, kws in CATEGORY_MAPPINGS.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                    if not reason_kw:
                        reason_kw = kw
                        
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
        reason = f"Classified because description explicitly mentions '{reason_kw}'."
    elif len(matched_cats) > 1:
        # False confidence fallback
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous complaint matching multiple descriptions like '{reason_kw}'."
    else:
        # Empty or ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No matching category keywords found in root text."
        
    row['category'] = category
    row['priority'] = priority
    row['reason'] = reason
    row['flag'] = flag
    
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row gracefully, write restricted results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        sys.exit(1)
        
    out_fieldnames = ['id', 'category', 'priority', 'reason', 'flag']
            
    results = []
    for r in rows:
        try:
            classified = classify_complaint(r)
            out_row = {
                'id': r.get('complaint_id', ''),
                'category': classified.get('category', ''),
                'priority': classified.get('priority', ''),
                'reason': classified.get('reason', ''),
                'flag': classified.get('flag', '')
            }
            results.append(out_row)
        except Exception:
            out_row = {
                'id': r.get('complaint_id', ''),
                'category': 'Other',
                'priority': 'Standard',
                'reason': 'Exception during row classification.',
                'flag': 'NEEDS_REVIEW'
            }
            results.append(out_row)
            
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
