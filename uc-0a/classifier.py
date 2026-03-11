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

    complaint_id = row.get("complaint_id", "").strip()
    text = (row.get("complaint_text", "") or "").lower()

    category = "general"
    priority = "low"
    reason = ""
    flag = ""

    if not text:
        flag = "NULL_TEXT"
        reason = "Complaint text missing"
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    if any(word in text for word in ["water", "leak", "pipeline"]):
        category = "water"
        priority = "medium"
        reason = "Water related complaint"

    elif any(word in text for word in ["garbage", "waste", "trash"]):
        category = "sanitation"
        priority = "medium"
        reason = "Sanitation issue"

    elif any(word in text for word in ["road", "pothole", "street"]):
        category = "roads"
        priority = "high"
        reason = "Road damage complaint"

    else:
        category = "other"
        priority = "low"
        reason = "General complaint"

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

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "",
                    "priority": "",
                    "reason": "",
                    "flag": f"ERROR: {str(e)}"
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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