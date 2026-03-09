"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]

CATEGORY_KEYWORDS = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "streetlight": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage"
}


def classify_complaint(row):

    description = row.get("description", "").lower()

    category = "Other"
    flag = ""

    for key, value in CATEGORY_KEYWORDS.items():
        if key in description:
            category = value
            break

    priority = "Standard"

    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            break

    reason = f"Detected keywords in description: {description[:50]}"

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):

    with open(input_path, newline='', encoding="utf-8") as infile, \
         open(output_path, "w", newline='', encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception:
                writer.writerow({
                    "complaint_id": row.get("complaint_id"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row processing failed",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print("Classification complete.")