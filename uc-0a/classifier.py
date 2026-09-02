"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


ALLOWED_CATEGORIES = [
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

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
    description = str(row.get("description", "") or "").strip()
    text = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is empty, so the complaint cannot be classified.",
            "flag": "NEEDS_REVIEW",
        }

    # Specific rules first.
    if "drain blocked" in text or "blocked drain" in text:
        category = "Drain Blockage"
        reason = "The complaint is classified as Drain Blockage because the description says 'drain blocked'."
        flag = ""

    elif "playing music" in text or "past midnight" in text:
        category = "Noise"
        reason = "The complaint is classified as Noise because the description mentions 'playing music' and 'past midnight'."
        flag = ""

    elif (
        "road surface cracked" in text
        or "road surface" in text
        or "sinking" in text
        or "broken footpath" in text
        or "footpath tiles broken" in text
    ):
        category = "Road Damage"
        reason = "The complaint is classified as Road Damage because the description mentions 'road surface' and damage."
        flag = ""

    elif "dead animal" in text or "animal not removed" in text:
        category = "Waste"
        reason = "The complaint is classified as Waste because the description mentions a 'dead animal' that was not removed."
        flag = ""

    elif "pothole" in text:
        category = "Pothole"
        reason = "The complaint is classified as Pothole because the description contains the word 'pothole'."
        flag = ""

    elif "flood" in text or "waterlogged" in text or "standing water" in text:
        category = "Flooding"
        reason = "The complaint is classified as Flooding because the description contains the word 'flood'."
        flag = ""

    elif (
        "streetlight" in text
        or "street light" in text
        or "lamp post" in text
        or "lights out" in text
    ):
        category = "Streetlight"
        reason = "The complaint is classified as Streetlight because the description mentions 'streetlight' or lights being out."
        flag = ""

    elif (
        "garbage" in text
        or "waste" in text
        or "trash" in text
        or "rubbish" in text
    ):
        category = "Waste"
        reason = "The complaint is classified as Waste because the description contains a waste-related term."
        flag = ""

    elif "noise" in text or "loud" in text or "sound pollution" in text:
        category = "Noise"
        reason = "The complaint is classified as Noise because the description contains a noise-related term."
        flag = ""

    elif (
        "heritage" in text
        or "monument" in text
        or "historic building" in text
    ):
        category = "Heritage Damage"
        reason = "The complaint is classified as Heritage Damage because the description contains the word 'heritage'."
        flag = ""

    elif (
        "heat" in text
        or "heatwave" in text
        or "extreme temperature" in text
    ):
        category = "Heat Hazard"
        reason = "The complaint is classified as Heat Hazard because the description contains a heat-related term."
        flag = ""

    elif "drainage" in text or "drain" in text:
        category = "Drain Blockage"
        reason = "The complaint is classified as Drain Blockage because the description contains the word 'drain'."
        flag = ""

    else:
        category = "Other"
        reason = "The description does not contain enough specific information to determine a category."
        flag = "NEEDS_REVIEW"

    # Severity keywords always make the complaint Urgent.
    severity_matches = [
        keyword for keyword in SEVERITY_KEYWORDS if keyword in text
    ]

    priority = "Urgent" if severity_matches else "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []

    for index, row in enumerate(rows, start=1):
        if not row.get("complaint_id"):
            row["complaint_id"] = f"ROW-{index}"

        results.append(classify_complaint(row))

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A citizen complaint classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Classification complete. Output written to {args.output}")