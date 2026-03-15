"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste",
    "Noise", "Road Damage", "Heritage Damage",
    "Heat Hazard", "Drain Blockage", "Other"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint = row.get("complaint", "").lower()
    complaint_id = row.get("complaint_id", "")

    category = "Other"
    priority = "Standard"
    flag = ""

    if "pothole" in complaint:
        category = "Pothole"
    elif "flood" in complaint:
        category = "Flooding"
    elif "light" in complaint:
        category = "Streetlight"
    elif "waste" in complaint or "garbage" in complaint:
        category = "Waste"
    elif "noise" in complaint:
        category = "Noise"
    elif "road" in complaint:
        category = "Road Damage"
    elif "heritage" in complaint:
        category = "Heritage Damage"
    elif "heat" in complaint:
        category = "Heat Hazard"
    elif "drain" in complaint:
        category = "Drain Blockage"

    for word in URGENT_KEYWORDS:
        if word in complaint:
            priority = "Urgent"

    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = f"Detected keywords from complaint: {complaint}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    #Read input CSV, classify each row, write results CSV.

    with open(input_path, "r") as infile, open(output_path, "w", newline="") as outfile:
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
                    "reason": "Row processing error",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")