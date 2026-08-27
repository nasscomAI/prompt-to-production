"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole": ["pothole", "crater", "hole"],
    "Flooding": ["flood", "waterlog", "submerge", "overflow", "water"],
    "Streetlight": ["streetlight", "street light", "bulb", "dark", "no light"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump"],
    "Noise": ["noise", "loud", "music", "party", "barking"],
    "Road Damage": ["road damage", "crack", "broken road", "cave-in"],
    "Heritage Damage": ["heritage", "monument", "historic", "ruin"],
    "Heat Hazard": ["heat", "sun", "blistering", "temperature"],
    "Drain Blockage": ["drain", "sewer", "clog", "block"]
}

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get('description', '')).lower()
    complaint_id = row.get('complaint_id', 'UNKNOWN')

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description is entirely missing or blank.",
            "flag": "NEEDS_REVIEW"
        }

    matched_category = "Other"
    matched_keyword = ""

    for category, keywords in ALLOWED_CATEGORIES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', description):
                matched_category = category
                matched_keyword = kw
                break
        if matched_category != "Other":
            break

    priority = "Standard"
    urgent_keyword = ""
    for ukw in URGENT_KEYWORDS:
        if re.search(r'\b' + re.escape(ukw) + r'\b', description):
            priority = "Urgent"
            urgent_keyword = ukw
            break

    flag = "NEEDS_REVIEW" if matched_category == "Other" else ""

    if matched_category == "Other":
        reason = "Category could not be confidently determined from the description alone."
    else:
        reason = f"Classified as {matched_category} because the description contains the word '{matched_keyword}'."
        if priority == "Urgent":
            reason = reason.rstrip('.') + f", and marked Urgent due to severity keyword '{urgent_keyword}'."

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
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
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    # Do not crash on bad rows, enforce missing data output gracefully
                    continue

        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error during batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
