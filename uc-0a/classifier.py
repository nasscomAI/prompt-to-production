"""
UC-0A — Complaint Classifier
Rule-engine based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water"],
    "Streetlight": ["streetlight", "dark", "light"],
    "Waste": ["garbage", "waste", "smell", "animal", "bin"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["cracked", "sinking", "manhole", "breaking"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "sun"],
    "Drain Blockage": ["drain blocked", "clogged drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with all original keys plus: category, priority, reason, flag
    """
    description = row.get('description', '')
    desc_lower = description.lower()
    
    # 1. Determine Priority
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            priority = "Urgent"
            break
            
    # 2. Determine Category and Reason
    matched_categories = []
    reason_kw = None
    
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    reason_kw = kw
    
    flag = ""
    reason = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason = f"Description explicitly cites '{reason_kw}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(matched_categories) > 1:
            reason = "Description contains keywords across multiple categories."
        else:
            reason = "Description does not match known category keywords."

    # Return merged dict
    return {
        **row,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV safely.
    """
    rows = []
    
    # Phase 1: Read and classify
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    rows.append(classified_row)
                except Exception as e:
                    # Graceful error failure for a row
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Error during processing: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                    rows.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        sys.exit(1)

    # Phase 2: Write output safely
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
