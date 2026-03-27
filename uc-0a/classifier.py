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

    text = row.get("complaint_text", "").lower()

    category = "general"
    priority = "low"
    reason = "general complaint"
    flag = "no"

    if not text:
        flag = "missing_text"
        reason = "complaint text missing"

    elif "refund" in text or "payment" in text:
        category = "billing"
        priority = "high"
        reason = "payment issue"

    elif "delay" in text or "late" in text:
        category = "service"
        priority = "medium"
        reason = "service delay"

    elif "rude" in text or "bad service" in text:
        category = "customer_service"
        priority = "high"
        reason = "staff behaviour issue"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must not crash on bad rows.
    """

    results = []

    with open(input_path, "r") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id"),
                    "category": "error",
                    "priority": "low",
                    "reason": "processing error",
                    "flag": "error"
                })

    with open(output_path, "w", newline="") as outfile:
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
