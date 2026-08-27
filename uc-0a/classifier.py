"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()

    category = "Other"
    priority = "Standard"
    flag = ""

    if "pothole" in text:
        category = "Pothole"

    elif "flood" in text:
        category = "Flooding"

    elif "streetlight" in text:
        category = "Streetlight"

    elif "garbage" in text or "waste" in text:
        category = "Waste"

    elif "noise" in text:
        category = "Noise"

    elif "road damage" in text:
        category = "Road Damage"

    elif "heritage" in text:
        category = "Heritage Damage"

    elif "heat" in text:
        category = "Heat Hazard"

    elif "drain" in text:
        category = "Drain Blockage"

    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    reason = f"Based on description keywords: {description[:40]}"

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

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Processing error",
                        "flag": "NEEDS_REVIEW"
                    }

                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
