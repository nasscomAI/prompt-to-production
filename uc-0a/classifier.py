"""
UC-0A — Complaint Classifier
Simple implementation for the assignment.
"""

import argparse
import csv


def classify_complaint(row: dict) -> dict:
    text = (row.get("complaint", "")).lower()

    if "error" in text or "issue" in text:
        category = "technical issue"
        priority = "high"
    elif "refund" in text or "payment" in text:
        category = "billing issue"
        priority = "medium"
    elif "account" in text or "login" in text:
        category = "account support"
        priority = "medium"
    else:
        category = "general query"
        priority = "low"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": "keyword based classification",
        "flag": "no"
    }


def batch_classify(input_path: str, output_path: str):

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []

    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "unknown",
                "priority": "low",
                "reason": str(e),
                "flag": "yes"
            })

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")