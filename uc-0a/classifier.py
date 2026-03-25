import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "UNKNOWN")
    text = row.get("complaint", "").lower()

    category = "Other"
    priority = "Normal"
    reason = ""
    flag = ""

    if not text.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty complaint",
            "flag": "NEEDS_REVIEW"
        }

    # Category classification
    if any(word in text for word in ["water", "leak", "pipe"]):
        category = "Water Issue"
        reason = "Detected keywords: water/leak/pipe"
    elif any(word in text for word in ["road", "pothole"]):
        category = "Road Issue"
        reason = "Detected keywords: road/pothole"
    elif any(word in text for word in ["garbage", "waste", "trash"]):
        category = "Garbage Issue"
        reason = "Detected keywords: garbage/waste/trash/dirty/dust"
    else:
        category = "Other"
        reason = "No matching keywords"
        flag = "NEEDS_REVIEW"

    # Priority detection
    if any(word in text for word in ["injury", "child", "hospital", "accident"]):
        priority = "Urgent"
    elif any(word in text for word in ["delay", "slow"]):
        priority = "Medium"
    else:
        priority = "Normal"

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

    with open(input_path, mode='r') as infile, open(output_path, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")