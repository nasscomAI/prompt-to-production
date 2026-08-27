import argparse
import csv

def classify_complaint(row):
    try:
        complaint_text = str(row.get("complaint", "")).lower()

        if not complaint_text.strip():
            return {
                "complaint_id": row.get("complaint_id", "unknown"),
                "category": "Unknown",
                "priority": "Low",
                "reason": "Empty complaint",
                "flag": "NULL_INPUT"
            }

        if "water" in complaint_text:
            category = "Plumbing"
            priority = "High"
            reason = "Water issue"
        elif "light" in complaint_text:
            category = "Electrical"
            priority = "Medium"
            reason = "Lighting issue"
        elif "garbage" in complaint_text:
            category = "Sanitation"
            priority = "Medium"
            reason = "Garbage issue"
        else:
            category = "General"
            priority = "Low"
            reason = "Other issue"

        return {
            "complaint_id": row.get("complaint_id", "unknown"),
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": "OK"
        }

    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id", "unknown"),
            "category": "Error",
            "priority": "Low",
            "reason": str(e),
            "flag": "ERROR"
        }


def batch_classify(input_path, output_path):
    results = []

    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            result = classify_complaint(row)
            results.append(result)

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print("Classification complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")