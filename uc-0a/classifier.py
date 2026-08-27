"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole","Flooding","Streetlight","Waste","Noise",
    "Road Damage","Heritage Damage","Heat Hazard",
    "Drain Blockage","Other"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood","waterlogging","water"],
    "Streetlight": ["streetlight","lamp","light"],
    "Waste": ["garbage","waste","trash","dump"],
    "Noise": ["noise","loud","music","construction"],
    "Road Damage": ["road damage","crack","broken road","bridge"],
    "Heritage Damage": ["heritage","monument","temple","statue"],
    "Heat Hazard": ["heat","hot","heatwave"],
    "Drain Blockage": ["drain","sewer","blockage"]
}

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance",
    "fire","hazard","fell","collapse"
]


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").lower()
    complaint_id = row.get("complaint_id","")

    category = "Other"
    matched_word = ""

    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in description:
                category = cat
                matched_word = w
                break
        if category != "Other":
            break

    priority = "Standard"
    for w in SEVERITY_KEYWORDS:
        if w in description:
            priority = "Urgent"
            matched_word = w
            break

    if priority != "Urgent":
        priority = "Low" if "minor" in description else "Standard"

    reason = "Detected keyword '{}' in description".format(matched_word) if matched_word else "No clear keyword detected"

    flag = ""
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

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    fieldnames = ["complaint_id","category","priority","reason","flag"]

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id",""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")

    args = parser.parse_args()
    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")

