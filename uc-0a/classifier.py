"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint = row.get("complaint", "").strip().lower()

    if complaint == "":
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Unknown",
            "priority": "Low",
            "reason": "Complaint text missing",
            "flag": "NULL_COMPLAINT"
        }

    # Category classification
    if "water" in complaint:
        category = "Water"

    elif "road" in complaint or "pothole" in complaint:
        category = "Road"

    elif "electric" in complaint or "power" in complaint:
        category = "Electricity"

    elif "garbage" in complaint or "waste" in complaint:
        category = "Sanitation"

    elif "drain" in complaint or "sewer" in complaint:
        category = "Drainage"

    else:
        category = "Other"

    # Priority classification
    urgent_words = [
        "urgent",
        "emergency",
        "immediately",
        "critical",
        "danger"
    ]

    priority = "Medium"

    for word in urgent_words:
        if word in complaint:
            priority = "High"
            break

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": "Keyword based classification",
        "flag": "OK"
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each complaint,
    and write results to output CSV.
    """

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag"
    ]

    with open(input_path, "r", newline="", encoding="utf-8") as infile, \
            open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:

            try:
                result = classify_complaint(row)
                writer.writerow(result)

            except Exception as e:

                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "ERROR",
                    "priority": "ERROR",
                    "reason": str(e),
                    "flag": "ERROR"
                })


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV"
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")