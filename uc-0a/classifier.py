
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water"],
    "Streetlight": ["streetlight", "light"],
    "Waste": ["garbage", "waste", "trash"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road damage", "crack", "broken road"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain", "sewage"]
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description",
            "flag": "NEEDS_REVIEW"
        }

    # Category detection
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for k in keywords:
            if k in description:
                category = cat
                reason = f"Keyword '{k}' found in description"
                break
        if category != "Other":
            break

    # Priority detection
    for s in SEVERITY_KEYWORDS:
        if s in description:
            priority = "Urgent"
            reason = f"Severity keyword '{s}' detected"
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason if reason else "No strong keyword match",
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

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
                    "reason": "Classification error",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
