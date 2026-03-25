import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    urgent = any(word in desc for word in ["injury", "child", "school", "hospital"])
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": "Other",
        "priority": "Urgent" if urgent else "Normal",
        "reason": "Found keyword" if urgent else "Normal issue",
        "flag": "REVIEW" if not urgent else ""
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        for row in reader:
            res = classify_complaint(row)
            writer.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
