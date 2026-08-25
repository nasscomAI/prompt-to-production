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
    """Classify one complaint row."""

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    # Handle missing descriptions safely.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so the complaint cannot be classified reliably.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Determine priority independently from category.
    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Determine category.
    # Specific categories are checked before broader categories.
    if "pothole" in text:
        category = "Pothole"
        reason = "The description contains the word 'pothole'."

    elif (
        "drain blocked" in text
        or "drain block" in text
        or ("drain" in text and "blocked" in text)
    ):
        category = "Drain Blockage"
        reason = "The description states that the drain is blocked."

    elif "flood" in text or "flooded" in text or "floods" in text:
        category = "Flooding"
        reason = "The description contains the word 'flooded' or another flooding-related term."

    elif "streetlight" in text or "streetlights" in text:
        category = "Streetlight"
        reason = "The description mentions 'streetlight' or 'streetlights'."

    elif (
        "garbage" in text
        or "waste" in text
        or "dumped" in text
        or "dead animal" in text
    ):
        category = "Waste"
        reason = "The description mentions waste-related material such as 'garbage', 'dumped', or 'dead animal'."

    elif "music" in text or "noise" in text:
        category = "Noise"
        reason = "The description mentions music or noise."

    elif "heat" in text or "hot" in text or "temperature" in text:
        category = "Heat Hazard"
        reason = "The description contains a heat-related concern."

    elif "heritage" in text and (
        "damage" in text
        or "damaged" in text
        or "broken" in text
    ):
        category = "Heritage Damage"
        reason = "The description mentions a damaged or broken heritage feature."

    elif (
        "road surface" in text
        or "road damage" in text
        or "cracked" in text
        or "sinking" in text
        or "broken" in text
        or "upturned" in text
    ):
        category = "Road Damage"
        reason = "The description mentions road or surface damage such as 'cracked' or 'sinking'."

    else:
        category = "Other"
        reason = "The description does not clearly match one of the defined complaint categories."

    # Flag genuinely ambiguous categories.
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # Safety check: category must always be allowed.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The complaint could not be assigned to an allowed category."

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

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)

            except Exception as exc:
                complaint_id = str(
                    row.get("complaint_id", "")
                ).strip()

                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed safely because of invalid input: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }

            results.append(result)

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

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

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )
