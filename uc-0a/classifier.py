import argparse
import csv

def classify_complaint(row: dict) -> dict:
    text = row.get("complaint", "").lower()

    if "pothole" in text:
        category = "Pothole"
        priority = "Standard"
        reason = "Contains pothole keyword"
        flag = ""
    elif "water" in text or "flood" in text:
        category = "Flooding"
        priority = "Standard"
        reason = "Water related issue"
        flag = ""
    elif "light" in text:
        category = "Streetlight"
        priority = "Standard"
        reason = "Streetlight issue"
        flag = ""
    elif "garbage" in text or "waste" in text:
        category = "Waste"
        priority = "Standard"
        reason = "Garbage related issue"
        flag = ""
    elif "noise" in text:
        category = "Noise"
        priority = "Standard"
        reason = "Noise complaint"
        flag = ""
    elif "road" in text:
        category = "Road Damage"
        priority = "Standard"
        reason = "Road related issue"
        flag = ""
    else:
        category = "Other"
        priority = "Low"
        reason = "No matching keyword"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing row",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")