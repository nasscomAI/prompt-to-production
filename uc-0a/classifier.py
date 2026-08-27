"""
UC-0A — Complaint Classifier
Updated file based on agents.md and skills.md.
"""
import argparse
import csv

# Allowed categories and severity keywords
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ["urgent", "immediate", "critical", "severe", "important"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Args:
        row (dict): A dictionary representing a single complaint row with fields like `description`.

    Returns:
        dict: A dictionary with keys: complaint_id, category, priority, reason, flag.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    # Default values
    category = "Other"
    priority = "Low"
    reason = ""
    flag = ""

    # Determine category based on keywords in description
    for cat in ALLOWED_CATEGORIES:
        if cat.lower() in description:
            category = cat
            reason = f"Matched category keyword: {cat}"
            break

    # Determine priority based on severity keywords
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category != "Other":
        priority = "Standard"

    # Set flag if category is ambiguous
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Args:
        input_path (str): Path to the input CSV file.
        output_path (str): Path to the output CSV file.

    Returns:
        None
    """
    with open(input_path, mode="r", encoding="utf-8") as infile, \
         open(output_path, mode="w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                classified_row = classify_complaint(row)
                writer.writerow(classified_row)
            except Exception as e:
                # Log error and skip problematic row
                print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
