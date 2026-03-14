"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = row.get("description", "")
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    # Category enforcement
    for cat in ALLOWED_CATEGORIES[:-1]:  # Exclude 'Other'
        if cat.lower() in description.lower():
            category = cat
            break

    # Priority enforcement
    if any(word in description.lower() for word in SEVERITY_KEYWORDS):
        priority = "Urgent"

    # Reason enforcement
    reason = f'Cited: {", ".join([word for word in SEVERITY_KEYWORDS if word in description.lower()])}' if priority == "Urgent" else f'Cited: {category}'

    # Flag enforcement
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline='') as infile, open(output_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            result = classify_complaint(row)
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
