"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    text = row.get("complaint_text", "").lower()
    complaint_id = row.get("complaint_id", "unknown")

    category = "general"
    priority = "low"
    reason = ""
    flag = ""

    if not text:
        flag = "missing_text"
        reason = "Complaint text missing"
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    if "garbage" in text or "trash" in text:
        category = "sanitation"
        reason = "Garbage related complaint"

    elif "road" in text or "pothole" in text:
        category = "roads"
        reason = "Road infrastructure issue"

    elif "water" in text or "pipeline" in text:
        category = "water"
        reason = "Water supply issue"

    elif "electricity" in text or "power" in text:
        category = "electricity"
        reason = "Electricity problem"

    else:
        category = "other"
        reason = "Uncategorized complaint"

    if "hospital" in text or "school" in text or "child" in text:
        priority = "high"
    else:
        priority = "medium"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify rows, write output CSV
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
                    "complaint_id": row.get("complaint_id", "unknown"),
                    "category": "error",
                    "priority": "low",
                    "reason": str(e),
                    "flag": "row_error"
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
