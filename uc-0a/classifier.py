"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    text = str(row).lower()

    if "broken" in text or "damaged" in text:
        category = "Damaged Product"
        priority = "High"
        reason = "Product damage complaint"
        flag = True

    elif "late" in text or "delay" in text:
        category = "Delivery Issue"
        priority = "Medium"
        reason = "Delivery delay complaint"
        flag = True

    else:
        category = "General Complaint"
        priority = "Low"
        reason = "General issue"
        flag = False

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }
    
    

def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)

            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Error",
                    "priority": "Low",
                    "reason": str(e),
                    "flag": False
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        writer.writerows(results)
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
