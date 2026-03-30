import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Low"
    reason = ""
    flag = ""

    # Category detection (basic keyword mapping)
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"
    elif "light" in description:
        category = "Streetlight"
    elif "garbage" in description or "waste" in description:
        category = "Waste"
    elif "noise" in description:
        category = "Noise"
    elif "road" in description:
        category = "Road Damage"
    elif "drain" in description:
        category = "Drain Blockage"
    elif "heat" in description:
        category = "Heat Hazard"

    # Priority detection
    if any(word in description for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Flag ambiguous cases
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Reason (must include words from description)
    reason = f"Based on keywords found in description: '{description[:50]}'"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:

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
                    "reason": "Error processing complaint",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")