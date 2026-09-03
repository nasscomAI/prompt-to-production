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
    """Classify one citizen complaint."""

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    # Missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # -------------------------
    # CATEGORY CLASSIFICATION
    # -------------------------

    if "pothole" in description_lower:
        category = "Pothole"
        evidence = "pothole"

    elif "flood" in description_lower:
        category = "Flooding"
        evidence = "flood"

    elif (
        "streetlight" in description_lower
        or "street light" in description_lower
        or "unlit" in description_lower
        or "darkness" in description_lower
    ):
        category = "Streetlight"
        evidence = "streetlight"

    elif (
        "garbage" in description_lower
        or "waste" in description_lower
        or "bins" in description_lower
    ):
        category = "Waste"
        evidence = "waste"

    elif (
        "music" in description_lower
        or "noise" in description_lower
        or "amplifier" in description_lower
        or "amplifiers" in description_lower
        or "wedding band" in description_lower
    ):
        category = "Noise"
        evidence = "music/noise"

    elif "heritage" in description_lower:
        category = "Heritage Damage"
        evidence = "heritage"

    elif (
        "heat" in description_lower
        or "temperature" in description_lower
        or "°c" in description_lower
        or "°c" in description_lower.replace(" ", "")
        or "heatwave" in description_lower
        or "sun" in description_lower
    ):
        category = "Heat Hazard"
        evidence = "heat/temperature"

    elif (
        "road surface" in description_lower
        or "road subsided" in description_lower
        or "road buckled" in description_lower
        or "road damage" in description_lower
        or "cobblestones broken" in description_lower
        or "tiles" in description_lower
        or "footpath broken" in description_lower
        or "paving removed" in description_lower
    ):
        category = "Road Damage"
        evidence = "road surface/damage"

    elif (
        "drain" in description_lower
        or "manhole" in description_lower
        or "draining directly" in description_lower
    ):
        category = "Drain Blockage"
        evidence = "drain"

    else:
        category = "Other"
        evidence = ""

    # -------------------------
    # PRIORITY CLASSIFICATION
    # -------------------------

    matched_keywords = []

    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            matched_keywords.append(keyword)

    if matched_keywords:
        priority = "Urgent"
        reason = (
            f'The description contains "{matched_keywords[0]}", '
            f'which requires Urgent priority.'
        )
    else:
        priority = "Standard"

        if category == "Other":
            reason = (
                "The description does not clearly match an allowed "
                "category, so it needs review."
            )
        else:
            reason = (
                f'The description contains "{evidence}", '
                f'supporting the {category} category.'
            )

    # -------------------------
    # AMBIGUITY FLAG
    # -------------------------

    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # -------------------------
    # FINAL VALIDATION
    # -------------------------

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ["Urgent", "Standard", "Low"]:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify every row, and write output CSV."""

    results = []

    try:
        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as infile:

            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    result = classify_complaint(row)

                except Exception:
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Unable to classify this complaint.",
                        "flag": "NEEDS_REVIEW",
                    }

                results.append(result)

    except Exception:
        results.append({
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "Unable to read the input file.",
            "flag": "NEEDS_REVIEW",
        })

    # -------------------------
    # WRITE OUTPUT CSV
    # -------------------------

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag",
        ]

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_[city].csv"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV"
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")