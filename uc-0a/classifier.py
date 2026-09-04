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

    description = str(
        row.get("description", row.get("complaint", ""))
    ).strip()

    text = description.lower()

    category = "Other"
    matched_phrase = ""

    # CATEGORY CLASSIFICATION

    if "pothole" in text:
        category = "Pothole"
        matched_phrase = "pothole"

    elif "flood" in text or "flooded" in text:
        category = "Flooding"

        if "flooded" in text:
            matched_phrase = "flooded"
        else:
            matched_phrase = "flood"

    elif (
        "streetlight" in text
        or "street light" in text
        or "lights out" in text
    ):
        category = "Streetlight"

        if "streetlight" in text:
            matched_phrase = "streetlight"
        elif "street light" in text:
            matched_phrase = "street light"
        else:
            matched_phrase = "lights out"

    elif (
        "garbage" in text
        or "waste" in text
        or "trash" in text
        or "dead animal" in text
        or "bulk waste" in text
    ):
        category = "Waste"

        if "dead animal" in text:
            matched_phrase = "dead animal"
        elif "bulk waste" in text:
            matched_phrase = "bulk waste"
        elif "garbage" in text:
            matched_phrase = "garbage"
        elif "waste" in text:
            matched_phrase = "waste"
        else:
            matched_phrase = "trash"

    elif (
        "noise" in text
        or "music past midnight" in text
        or "playing music" in text
    ):
        category = "Noise"

        if "music past midnight" in text:
            matched_phrase = "music past midnight"
        elif "playing music" in text:
            matched_phrase = "playing music"
        else:
            matched_phrase = "noise"

    elif (
        "road surface cracked" in text
        or "cracked and sinking" in text
        or "manhole cover missing" in text
        or "manhole" in text
        or "footpath tiles broken" in text
        or ("footpath" in text and "broken" in text)
        or ("road" in text and "damaged" in text)
    ):
        category = "Road Damage"

        if "manhole cover missing" in text:
            matched_phrase = "manhole cover missing"
        elif "manhole" in text:
            matched_phrase = "manhole"
        elif "footpath tiles broken" in text:
            matched_phrase = "footpath tiles broken"
        elif "cracked and sinking" in text:
            matched_phrase = "cracked and sinking"
        elif "road surface cracked" in text:
            matched_phrase = "road surface cracked"
        else:
            matched_phrase = "damaged"

    elif "heritage" in text or "monument" in text:
        category = "Heritage Damage"

        if "heritage" in text:
            matched_phrase = "heritage"
        else:
            matched_phrase = "monument"

    elif (
        "heat" in text
        or "extreme temperature" in text
    ):
        category = "Heat Hazard"

        if "heat" in text:
            matched_phrase = "heat"
        else:
            matched_phrase = "extreme temperature"

    elif (
        "drain" in text
        or "drainage" in text
    ):
        category = "Drain Blockage"

        if "drain" in text:
            matched_phrase = "drain"
        else:
            matched_phrase = "drainage"

    # PRIORITY CLASSIFICATION

    matched_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    if matched_severity:
        priority = "Urgent"
        severity_phrase = matched_severity[0]
    else:
        priority = "Standard"
        severity_phrase = ""

    # FLAG AND REASON

    if category == "Other":
        flag = "NEEDS_REVIEW"

        reason = (
            f'The description "{description}" does not clearly '
            f'match an allowed category.'
        )

    else:
        flag = ""

        if matched_severity:
            reason = (
                f'The description contains "{matched_phrase}" '
                f'and "{severity_phrase}", so it matches '
                f'{category} and requires Urgent priority.'
            )
        else:
            reason = (
                f'The description contains "{matched_phrase}", '
                f'supporting the {category} category.'
            )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify every row, and write results."""

    results = []

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        for row in reader:
            try:
                results.append(
                    classify_complaint(row)
                )

            except Exception as error:
                complaint_id = row.get(
                    "complaint_id",
                    ""
                )

                results.append({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        f"Unable to classify this row safely: "
                        f"{error}."
                    ),
                    "flag": "NEEDS_REVIEW",
                })

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
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
        help="Path to input CSV"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV"
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output
    )

    print(
        f"Done. Results written to {args.output}"
    )