"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv

CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    reason = ""
    flag = ""

    if "pothole" in description:
        category = "Pothole"
        reason = "Description contains keyword 'pothole'"

    elif "flood" in description:
        category = "Flooding"
        reason = "Description contains keyword 'flood'"

    elif "streetlight" in description or "light not working" in description:
        category = "Streetlight"
        reason = "Description mentions streetlight issue"

    elif "garbage" in description or "waste" in description:
        category = "Waste"
        reason = "Description contains keyword 'garbage'"

    elif "noise" in description:
        category = "Noise"
        reason = "Description contains keyword 'noise'"

    elif "road damage" in description or "road broken" in description:
        category = "Road Damage"
        reason = "Description mentions road damage"

    elif "drain" in description:
        category = "Drain Blockage"
        reason = "Description mentions drain blockage"

    else:
        category = "Other"
        reason = "No known category keywords detected"
        flag = "NEEDS_REVIEW"

    priority = "Standard"

    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            reason += f"; severity keyword '{word}' detected"
            break

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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
                        "reason": "Row processing error",
                        "flag": "NEEDS_REVIEW",
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")