"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell",
    "collapse", "accident", "crash"
]

# Ordered from most specific → most general
CATEGORY_KEYWORDS = {
    "drain": "Drain Blockage",
    "mosquito": "Drain Blockage",
    "pothole": "Pothole",
    "collapse": "Road Damage",
    "crater": "Road Damage",
    "road": "Road Damage",
    "streetlight": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "drilling": "Noise",
    "engine": "Noise",
    "truck": "Noise",
    "idling": "Noise",
    "noise": "Noise",
    "flood": "Flooding",
    "water": "Flooding"
}


def classify_complaint(row):

    description = row.get("description", "").lower()

    category = "Other"
    matched_keyword = None
    flag = ""

    for keyword, value in CATEGORY_KEYWORDS.items():
        if keyword in description:
            category = value
            matched_keyword = keyword
            break

    priority = "Standard"
    urgency_trigger = None

    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            urgency_trigger = keyword
            break

    if matched_keyword:
        reason = f"keyword '{matched_keyword}' indicates {category.lower()}"
    else:
        reason = "no clear category keywords found"

    if urgency_trigger:
        reason += f"; urgency triggered by '{urgency_trigger}'"

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
                    "reason": "classification failed",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print("Classification complete.")