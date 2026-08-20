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

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Required severity keywords always force Urgent.
    matched_severity = [
        keyword for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    priority = "Urgent" if matched_severity else "Standard"

    # Category rules.
    if "pothole" in text:
        category = "Pothole"
        evidence = "pothole"

    elif "streetlight" in text or "street light" in text:
        category = "Streetlight"
        evidence = (
            "streetlight" if "streetlight" in text else "street light"
        )

    elif any(word in text for word in ["heritage", "historic", "monument"]):
        category = "Heritage Damage"
        evidence = next(
            word
            for word in ["heritage", "historic", "monument"]
            if word in text
        )

    elif "heat" in text or "extreme temperature" in text:
        category = "Heat Hazard"
        evidence = (
            "heat" if "heat" in text else "extreme temperature"
        )

    elif any(
        phrase in text
        for phrase in [
            "road surface",
            "damaged road",
            "cracked road",
            "road damage",
            "road sinking",
            "road is sinking",
        ]
    ):
        category = "Road Damage"
        evidence = next(
            phrase
            for phrase in [
                "road surface",
                "damaged road",
                "cracked road",
                "road damage",
                "road sinking",
                "road is sinking",
            ]
            if phrase in text
        )

    elif "manhole" in text:
        category = "Drain Blockage"
        evidence = "manhole"

    elif any(
        word in text
        for word in ["drain", "drainage", "blocked drain"]
    ) and not any(
        word in text
        for word in ["flood", "flooded", "flooding"]
    ):
        category = "Drain Blockage"
        evidence = next(
            word
            for word in ["drain", "drainage", "blocked drain"]
            if word in text
        )

    elif any(
        word in text
        for word in ["garbage", "waste", "rubbish", "trash", "dead animal"]
    ):
        category = "Waste"
        evidence = next(
            word
            for word in [
                "garbage",
                "waste",
                "rubbish",
                "trash",
                "dead animal",
            ]
            if word in text
        )

    elif any(word in text for word in ["noise", "loud", "music"]):
        category = "Noise"
        evidence = next(
            word
            for word in ["noise", "loud", "music"]
            if word in text
        )

    elif any(
        word in text
        for word in ["flood", "flooded", "flooding", "waterlogged"]
    ):
        category = "Flooding"
        evidence = next(
            word
            for word in [
                "flood",
                "flooded",
                "flooding",
                "waterlogged",
            ]
            if word in text
        )

    else:
        category = "Other"
        evidence = None

    # Ambiguous/unclassified complaints require review.
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = (
            "The description contains "
            f'"{description}" and does not clearly identify '
            "one of the allowed categories."
        )
    else:
        flag = ""
        reason = (
            f'The description contains "{evidence}", '
            f"indicating {category}."
        )

    # Defensive validation.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in {"Urgent", "Standard", "Low"}:
        priority = "Standard"

    if flag not in {"", "NEEDS_REVIEW"}:
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Classify every row and write the results to a CSV."""

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        input_path,
        newline="",
        encoding="utf-8",
    ) as infile:
        reader = csv.DictReader(infile)

        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as outfile:

            writer = csv.DictWriter(
                outfile,
                fieldnames=output_fields,
            )

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    result = {
                        "complaint_id": str(
                            row.get("complaint_id", "")
                        ).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "The row could not be classified "
                            "from valid input."
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
        help="Path to test_[city].csv",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")