"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Check severity for Urgent priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in desc for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Determine category
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["garbage", "waste", "dead animal", "smell"],
        "Noise": ["music", "noise"],
        "Road Damage": ["cracked", "sinking", "manhole", "broken", "footpath tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "drain"],
    }
    
    matches = []
    reason_word = None
    for cat, kws in categories.items():
        for kw in kws:
            if kw in desc:
                matches.append(cat)
                if not reason_word:
                    reason_word = kw
                break

    flag = ""
    if len(matches) == 1:
        category = matches[0]
    else:
        # Ambiguous or no matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    if category != "Other" and reason_word:
        reason = f"The description contains '{reason_word}' indicating a {category}."
    else:
        reason = "The category is genuinely ambiguous or could not be determined from the description alone."
        
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    if not row.get("description"):
                        res = {
                            "complaint_id": row.get("complaint_id", ""),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Description is missing.",
                            "flag": "NEEDS_REVIEW"
                        }
                    else:
                        res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error.",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    if results:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
