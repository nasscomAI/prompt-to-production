"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    text = row.get("complaint", "").lower()
    category = "unknown"
    priority = "low"
    reason = ""
    flag = ""

    if "pothole" in text:
        category = "pothole"
        priority = "high"
        reason = "Road safety issue"
    elif "streetlight" in text:
        category = "streetlight"
        priority = "medium"
        reason = "Public safety issue"
    elif "garbage" in text:
        category = "garbage"
        priority = "medium"
        reason = "Sanitation issue"
    elif "flood" in text or "waterlogging" in text:
        category = "flooding"
        priority = "high"
        reason = "Flood risk"

    if not text.strip():
        flag = "null complaint"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                row.update(result)
                writer.writerow(row)
            except Exception as e:
                row.update({"category": "error", "priority": "low", "reason": str(e), "flag": "processing_failed"})
                writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
