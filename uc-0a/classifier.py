"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint = row.get("complaint", "").lower()

    category = "other"
    priority = "normal"
    reason = "default rule"
    flag = ""

    if "garbage" in complaint or "waste" in complaint:
        category = "sanitation"
        reason = "garbage keyword"

    elif "road" in complaint or "pothole" in complaint:
        category = "roads"
        reason = "road keyword"

    elif "water" in complaint or "pipe" in complaint:
        category = "water"
        reason = "water keyword"

    elif "electric" in complaint or "power" in complaint:
        category = "electricity"
        reason = "electric keyword"

    if "accident" in complaint or "hospital" in complaint or "child" in complaint:
        priority = "high"
        flag = "urgent"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):

    with open(input_path, "r") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", newline="") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    print("Error processing row:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

