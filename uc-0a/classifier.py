"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    desc = row.get("description", "").lower()
    
    # Evaluate Priority
    priority_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    reason_word = None
    
    for kw in priority_keywords:
        if kw in desc:
            priority = "Urgent"
            reason_word = kw
            break
            
    # Evaluate Category
    category = "Other"
    category_map = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'streetlight': 'Streetlight',
        'light': 'Streetlight',
        'garbage': 'Waste',
        'waste': 'Waste',
        'animal': 'Waste',
        'music': 'Noise',
        'crack': 'Road Damage',
        'sink': 'Road Damage',
        'drain blocked': 'Drain Blockage',
        'manhole': 'Drain Blockage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard'
    }
    
    for kw, cat in category_map.items():
        if kw in desc:
            category = cat
            if not reason_word:
                reason_word = kw
            break
            
    # Set Flags & Reasons
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    reason_word = reason_word if reason_word else "unclear issue"
    reason = f"The description contains the word '{reason_word}'."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        for row in reader:
            try:
                classification = classify_complaint(row)
                row.update(classification)
                results.append(row)
            except Exception as e:
                print(f"Failed to process row {row.get('complaint_id')}: {e}")
                # Include unclassified row to avoid dropping data
                results.append(row)
                
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
