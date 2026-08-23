"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import sys

# Constants defined in agents.md
ALLOWED_CATEGORIES = {
    "Pothole": ["pothole", "crater", "dip"],
    "Flooding": ["flood", "water", "inundation", "overflow"],
    "Streetlight": ["light", "street light", "dark", "flicker"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud", "music", "construction"],
    "Road Damage": ["crack", "pavement", "broken road"],
    "Heritage Damage": ["heritage", "monument", "wall"],
    "Heat Hazard": ["heat", "hot", "thermal"],
    "Drain Blockage": ["drain", "clog", "blocked", "sewer"],
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description.
    """
    desc_lower = description.lower()
    
    # Determine Category
    category = "Other"
    reason = "Could not definitively determine category from description."
    flag = "NEEDS_REVIEW"
    
    for cat, keywords in ALLOWED_CATEGORIES.items():
        if any(k in desc_lower for k in keywords):
            category = cat
            reason = f"Classified as {cat} due to keyword match: {', '.join([k for k in keywords if k in desc_lower])}."
            flag = ""
            break
            
    # Determine Priority
    priority = "Standard"
    if any(k in desc_lower for k in URGENT_KEYWORDS):
        priority = "Urgent"
        # Add to reason if urgent
        urgent_matches = [k for k in URGENT_KEYWORDS if k in desc_lower]
        reason += f" Priority set to Urgent due to severity keyword(s): {', '.join(urgent_matches)}."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        description = row.get('description', '')
                        classification = classify_complaint(description)
                        row.update(classification)
                        writer.writerow(row)
                    except Exception as e:
                        print(f"Error processing row {row}: {e}", file=sys.stderr)
                        # Write row with failure flag if possible
                        row.update({'category': 'Other', 'priority': 'Standard', 'reason': 'Error processing row.', 'flag': 'NEEDS_REVIEW'})
                        writer.writerow(row)
    except Exception as e:
        print(f"Critical error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
