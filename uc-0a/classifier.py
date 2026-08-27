"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority Enforcement
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            break

    # Category Mapping & Enforcements
    categories = {
        "Pothole": ["pothole", "crater", "hole"],
        "Flooding": ["flood", "overflow", "waterlogging"],
        "Streetlight": ["light", "streetlight", "lamp", "dark"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump"],
        "Noise": ["noise", "loud", "music", "party", "sound"],
        "Road Damage": ["damage", "crack", "surface", "broken road"],
        "Heritage Damage": ["heritage", "monument", "historic", "statue"],
        "Heat Hazard": ["heat", "temperature", "sun"],
        "Drain Blockage": ["drain", "blockage", "clogged", "sewer"]
    }

    matches = []
    reason_word = "unknown"
    for cat, kws in categories.items():
        for kw in kws:
            if re.search(rf"\b{re.escape(kw)}\b", description):
                if cat not in matches:
                    matches.append(cat)
                    reason_word = kw
    
    # Flag and Reason Enforcements
    if len(matches) == 1:
        category = matches[0]
        flag = ""
        reason = f"Description mentions '{reason_word}'."
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous description matches multiple categories: {', '.join(matches)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not identify a clear category from the description."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "description": row.get("description", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results to output CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    results = []
    for i, row in enumerate(rows):
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "description": row.get("description", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Processing error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })

    if results:
        fieldnames = ["complaint_id", "description", "category", "priority", "reason", "flag"]
        try:
            with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
