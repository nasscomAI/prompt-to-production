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

ALLOWED_PRIORITIES = {
    "Urgent",
    "Standard",
    "Low",
}

URGENT_KEYWORDS = [
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
    """
    Classify one citizen complaint.

    Returns:
        complaint_id
        category
        priority
        reason
        flag
    """

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    # Handle missing descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Priority classification
    if any(keyword in text for keyword in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Category classification
    if "pothole" in text:
        category = "Pothole"
        reason = 'The description contains the specific word "pothole".'

    elif "flood" in text or "flooded" in text or "flooding" in text:
        category = "Flooding"
        reason = 'The description contains "flood", "flooded", or "flooding".'

    elif "drain" in text and (
        "blocked" in text or "blockage" in text or "blocked drain" in text
    ):
        category = "Drain Blockage"
        reason = 'The description mentions a blocked or blocked drain.'

    elif "streetlight" in text or "streetlights" in text:
        category = "Streetlight"
        reason = 'The description contains "streetlight" or "streetlights".'

    elif (
        "garbage" in text
        or "waste" in text
        or "dumped" in text
        or "dump" in text
    ):
        category = "Waste"
        reason = 'The description mentions garbage, waste, or dumped material.'

    elif "music" in text or "noise" in text:
        category = "Noise"
        reason = 'The description mentions music or noise.'

    elif (
        "road surface" in text
        or "road damage" in text
        or "cracked" in text
        or "sinking" in text
        or "broken" in text
        or "upturned" in text
    ):
        category = "Road Damage"
        reason = 'The description mentions cracked, sinking, broken, or damaged road infrastructure.'

    elif "heritage" in text:
        category = "Heritage Damage"
        reason = 'The description contains the specific word "heritage".'

    elif "heat" in text or "extreme temperature" in text:
        category = "Heat Hazard"
        reason = 'The description mentions heat or extreme temperature.'

    else:
        category = "Other"
        reason = 'The description contains terms such as "manhole" that do not match an allowed category.'

    # Ambiguous categories require review
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # Final schema enforcement
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read the input CSV, classify every complaint,
    and write the results to an output CSV.
    """

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline=""
        ) as outfile:

            writer = csv.DictWriter(
                outfile,
                fieldnames=output_fields
            )

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)

                except Exception as exc:
                    result = {
                        "complaint_id": str(
                            row.get("complaint_id", "")
                        ).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed: {exc}",
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

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )