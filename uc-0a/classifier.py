"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:

    complaint_id = row["complaint_id"]
    description = row["description"].lower()

    category = "other"
    priority = "low"
    reason = "no critical keywords"
    flag = "ok"

    if "pothole" in description or "collapsed" in description or "crater" in description:
        category = "road_damage"

    elif "flood" in description or "drain" in description or "blocked" in description:
        category = "water_logging"

    elif "garbage" in description or "waste" in description or "overflow" in description:
        category = "sanitation"

    if "ambulance" in description or "hospital" in description or "hospitalised" in description or "risk" in description or "school" in description:
        priority = "high"
        reason = "public safety risk"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }



def batch_classify(input_path: str, output_path: str):

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        results = []

        for row in reader:
            result = classify_complaint(row)
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
