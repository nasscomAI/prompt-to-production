"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
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


CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooding", "waterlogged", "water logging"],
    "Streetlight": ["streetlight", "street light", "lamp post"],
    "Waste": ["garbage", "waste", "trash", "rubbish"],
    "Noise": ["noise", "loud music", "loudspeaker"],
    "Road Damage": [
    "road damage",
    "damaged road",
    "broken road",
    "cracked road",
    "road surface",
    "cracked",
    "sinking",
    "footpath",
    "footpath tiles",
    "broken tiles"
],
    "Heritage Damage": ["heritage", "monument", "historic building"],
    "Heat Hazard": ["heatwave", "heat wave", "extreme heat", "heat hazard"],
    "Drain Blockage": ["drain blockage", "blocked drain", "drainage", "drain"],
}


def find_matching_keyword(text, keywords):
    """Return the first matching keyword found in the text."""
    for keyword in keywords:
        if keyword in text:
            return keyword
    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")

    description = (
        row.get("description")
        or row.get("complaint")
        or row.get("complaint_description")
        or ""
    ).strip()

    # Handle missing complaint descriptions safely.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Severity keywords always trigger Urgent.
    severity_keyword = find_matching_keyword(text, SEVERITY_KEYWORDS)

    if severity_keyword:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Find category and evidence.
    category = "Other"
    category_evidence = None

    for possible_category, keywords in CATEGORY_KEYWORDS.items():
        matched_keyword = find_matching_keyword(text, keywords)

        if matched_keyword:
            category = possible_category
            category_evidence = matched_keyword
            break

    # Ambiguous/unknown complaints require review.
    if category == "Other":
        flag = "NEEDS_REVIEW"

        # Use a short piece of the original description as evidence.
        evidence = description[:60].strip()

        if evidence:
            reason = (
                f"The description '{evidence}' does not provide enough "
                f"specific information for a canonical category."
            )
        else:
            reason = "The complaint description does not provide enough information."

    else:
        flag = ""

        reason = (
            f"The description contains '{category_evidence}', "
            f"supporting the '{category}' category."
        )

        if severity_keyword:
            reason += (
                f" It also contains '{severity_keyword}', "
                f"which requires Urgent priority."
            )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every row, and write results CSV.

    Individual bad rows must not stop the complete batch.
    """

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(input_path, "r", encoding="utf-8", newline="") as input_file:

        reader = csv.DictReader(input_file)

        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline=""
        ) as output_file:

            writer = csv.DictWriter(
                output_file,
                fieldnames=output_fields
            )

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)

                except Exception:
                    # Do not allow one bad row to crash the entire batch.
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "The complaint could not be classified "
                            "because of invalid input."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                writer.writerow(result)


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