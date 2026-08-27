"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row deterministically based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, description, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Allowed Categories and their keywords for deterministic matching
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "road": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }

    category = "Other"
    matched_word = ""
    for kw, cat in category_map.items():
        if kw in desc:
            category = cat
            matched_word = kw
            break

    # Flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # Priority
    priority = "Standard"
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_word = ""

    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            urgent_word = kw
            break
            
    if priority == "Standard" and category == "Other":
        priority = "Low"

    # Reason
    if category != "Other" and priority == "Urgent":
        reason = f"Classified as {category} based on '{matched_word}', and marked Urgent due to '{urgent_word}'."
    elif category != "Other":
        reason = f"Classified as {category} based on '{matched_word}' in description."
    else:
        reason = "Category is genuinely ambiguous."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "description": row.get("description", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "description", "category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        result = classify_complaint(row)
                        writer.writerow(result)
                    except Exception as e:
                        print(f"Error processing row: {row.get('complaint_id', 'unknown')}. Error: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
