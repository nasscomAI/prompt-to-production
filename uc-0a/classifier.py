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

    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Normal",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Category detection
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description:
        category = "Flooding"
    elif "garbage" in description or "trash" in description:
        category = "Garbage"
    elif "traffic" in description:
        category = "Traffic"
    elif "noise" in description:
        category = "Noise"
    elif "damage" in description or "broken" in description:
        category = "Infrastructure Damage"
    else:
        category = "Other"

    # Priority detection
    if "injury" in description or "child" in description or "school" in description:
        priority = "Urgent"
    else:
        priority = "Normal"

    reason = "Detected keywords in description"
    flag = ""

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
    """

    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Normal",
                    "reason": "Error processing row",
                    "flag": "NEEDS_REVIEW"
                }

            results.append(result)

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")