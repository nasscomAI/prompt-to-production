import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance",
    "fire","hazard","fell","collapse"
]

CATEGORIES = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "garbage": "Waste",
    "trash": "Waste",
    "waste": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "drain": "Drain Blockage",
    "heat": "Heat Hazard"
}


def classify_complaint(row: dict) -> dict:
    text = row.get("description", "").lower()

    category = "Other"
    for keyword, cat in CATEGORIES.items():
        if keyword in text:
            category = cat
            break

    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    reason = f"Detected keywords in description: {text[:50]}"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", newline='', encoding="utf-8") as outfile:
            fieldnames = ["complaint_id","category","priority","reason","flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id",""),
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