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

    complaint_id = row.get("complaint_id", "").strip()
    text = row.get("complaint", "").lower().strip()

    # Handle missing complaint
    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "unknown",
            "priority": "low",
            "reason": "Missing complaint text",
            "flag": "NULL_COMPLAINT"
        }

    # Category detection
    if any(word in text for word in ["garbage", "waste", "trash"]):
        category = "sanitation"
    elif any(word in text for word in ["water", "pipe", "leak"]):
        category = "water"
    elif any(word in text for word in ["road", "pothole", "street"]):
        category = "roads"
    elif any(word in text for word in ["electric", "power", "electricity"]):
        category = "electricity"
    else:
        category = "other"

    # Priority detection
    if any(word in text for word in ["hospital", "school", "child", "injury"]):
        priority = "high"
    elif any(word in text for word in ["urgent", "danger", "flood"]):
        priority = "medium"
    else:
        priority = "low"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": f"Detected keywords for {category}",
        "flag": ""
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        with open(output_path, "w", newline='', encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "error",
                        "priority": "low",
                        "reason": str(e),
                        "flag": "ROW_ERROR"
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")