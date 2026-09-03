"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


ALLOWED_CATEGORIES = {
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
}

URGENT_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}


def classify_complaint(row: dict) -> dict:
    """Classify a single citizen complaint."""

    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()
    description_lower = description.lower()

    # Handle missing descriptions safely.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing, so the complaint cannot be classified.",
            "flag": "NEEDS_REVIEW",
        }

    # Category classification.
    if "pothole" in description_lower:
        category = "Pothole"
    elif "flood" in description_lower or "flooded" in description_lower:
        category = "Flooding"
    elif "streetlight" in description_lower:
        category = "Streetlight"
    elif "garbage" in description_lower or "waste" in description_lower:
        category = "Waste"
    elif "music" in description_lower or "noise" in description_lower:
        category = "Noise"
    elif "heritage" in description_lower:
        category = "Heritage Damage"
    elif "drain" in description_lower:
        category = "Drain Blockage"
    elif (
        "road surface" in description_lower
        or "road" in description_lower
        or "manhole" in description_lower
        or "footpath" in description_lower
    ):
        category = "Road Damage"
    elif "heat" in description_lower:
        category = "Heat Hazard"
    else:
        category = "Other"

    # Priority classification.
    matched_keywords = [
        keyword
        for keyword in URGENT_KEYWORDS
        if keyword in description_lower
    ]

    if matched_keywords:
        priority = "Urgent"
        evidence = matched_keywords[0]
        reason = (
            f"The complaint describes a {category.lower()} issue and "
            f"cites the severity keyword '{evidence}'."
        )
    else:
        priority = "Standard"
        evidence = description.split(".")[0].strip()
        reason = f"The description states '{evidence}'."

    # Flag genuinely ambiguous classifications.
    flag = ""

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write results CSV."""

    results = []

    with open(input_path, "r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The complaint could not be classified from the provided input.",
                    "flag": "NEEDS_REVIEW",
                }

            results.append(result)

    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag",
        ]

        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Classify municipal citizen complaints."
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

    print(f"Results written to {args.output}")