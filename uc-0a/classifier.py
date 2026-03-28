import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance","fire","hazard","fell","collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood","waterlogging"],
    "Streetlight": ["streetlight","light"],
    "Waste": ["garbage","trash","waste"],
    "Noise": ["noise","loud"],
    "Road Damage": ["road damage","broken road"],
    "Heritage Damage": ["heritage","monument"],
    "Heat Hazard": ["heat","hot"],
    "Drain Blockage": ["drain","blocked drain"]
}


def classify_complaint(row: dict) -> dict:

    complaint_id = row.get("complaint_id","")
    description = row.get("description","").lower()

    category = "Other"
    flag = ""

    # category detection
    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in description:
                category = cat
                break

    # severity detection
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            break

    reason = f"Detected keywords in complaint: {description[:50]}"

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):

    results = []

    with open(input_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                continue

    with open(output_path, "w", newline='', encoding="utf-8") as f:
        fieldnames = ["complaint_id","category","priority","reason","flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")