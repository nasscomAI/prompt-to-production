"""
UC-0A — Complaint Classifier
Simple rule-based classifier for complaint descriptions
"""

import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Normal"
    reason = ""
    flag = ""

    # Category rules
    if "pothole" in description or "road damage" in description:
        category = "Pothole"
        reason = "Detected words related to pothole or road damage"
    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"
        reason = "Detected flooding related keywords"
    elif "garbage" in description or "waste" in description:
        category = "Garbage"
        reason = "Detected garbage or waste keywords"
    elif "streetlight" in description or "light not working" in description:
        category = "Streetlight"
        reason = "Detected streetlight issue keywords"
    elif "water supply" in description or "no water" in description:
        category = "Water Supply"
        reason = "Detected water supply issue keywords"
    else:
        category = "Other"
        reason = "Category not clearly identified from description"
        flag = "NEEDS_REVIEW"

    # Priority rules
    urgent_words = ["injury", "danger", "accident", "hospital", "school"]

    for word in urgent_words:
        if word in description:
            priority = "Urgent"
            reason += f"; urgent keyword detected: {word}"
            break

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles bad rows and continues processing.
    """

    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Error",
                    "priority": "Normal",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "FAILED_ROW"
                })

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