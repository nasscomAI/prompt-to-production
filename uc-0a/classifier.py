"""
UC-0A — Complaint Classifier
"""

import argparse
import csv


# Exact categories from README
CATEGORIES = {
    "Pothole": [
        "pothole",
        "crater",
        "bump in road",
    ],
    "Flooding": [
        "flood",
        "flooded",
        "flooding",
        "water logging",
        "waterlogged",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "lights out",
        "lamp post",
        "lamp",
        "flickering light",
        "flickering",
    ],
    "Waste": [
        "waste",
        "garbage",
        "trash",
        "litter",
        "dumped",
        "dump",
        "dead animal",
    ],
    "Noise": [
        "noise",
        "loud",
        "sound",
        "music",
        "playing music",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracks in road",
        "cracked",
        "cracked road",
        "road surface",
        "sinking",
        "manhole",
        "footpath",
        "broken tiles",
        "upturned",
    ],
    "Heritage Damage": [
        "heritage damage",
        "historical site damage",
        "monument damage",
        "damaged monument",
    ],
    "Heat Hazard": [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
    ],
    "Drain Blockage": [
        "drain blockage",
        "clogged drain",
        "sewer block",
        "blocked drain",
        "drain blocked",
    ],
}


# Exact severity keywords from README
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

    complaint_id = row.get("complaint_id", "")
    description = str(row.get("description", "") or "").strip()
    description_lower = description.lower()

    # Empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description is empty, so it needs review.",
            "flag": "NEEDS_REVIEW",
        }

    matches = []

    # Find matching categories
    for category_name, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in description_lower:
                matches.append((category_name, keyword))
                break

    # Remove duplicate category names
    matched_categories = list(
        dict.fromkeys(category for category, keyword in matches)
    )

    category = "Other"
    flag = ""
    reason = ""

    # No category match
    if len(matched_categories) == 0:

        category = "Other"
        flag = "NEEDS_REVIEW"

        reason = (
            "The description does not contain a specific category indicator, "
            "so it needs review."
        )

    # Exactly one category match
    elif len(matched_categories) == 1:

        category, keyword = matches[0]

        reason = (
            f'The description contains "{keyword}", '
            f'which indicates {category}.'
        )

    # Multiple categories = genuinely ambiguous
    else:

        category = "Other"
        flag = "NEEDS_REVIEW"

        matched_words = [
            keyword for _, keyword in matches
        ]

        reason = (
            f'The description contains multiple category indicators: '
            f'"{", ".join(matched_words)}", so it needs review.'
        )

    # Default priority
    priority = "Standard"
    severity_match = None

    # Severity keywords trigger Urgent
    for keyword in SEVERITY_KEYWORDS:

        if keyword in description_lower:
            priority = "Urgent"
            severity_match = keyword
            break

    # Add severity reason
    if severity_match:

        reason = reason.rstrip(".") + (
            f'. It also contains "{severity_match}", '
            f'so priority is Urgent.'
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify rows, and write output CSV."""

    output_rows = []

    with open(
        input_path,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as infile:

        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        # Preserve original columns
        original_fields = [
            field
            for field in reader.fieldnames
            if field not in [
                "category",
                "priority",
                "reason",
                "flag",
            ]
        ]

        # Required output columns
        fieldnames = original_fields + [
            "category",
            "priority",
            "reason",
            "flag",
        ]

        for row_number, row in enumerate(reader, start=1):

            try:

                classified = classify_complaint(row)

                output_row = {
                    field: row.get(field, "")
                    for field in original_fields
                }

                output_row.update({
                    "category": classified["category"],
                    "priority": classified["priority"],
                    "reason": classified["reason"],
                    "flag": classified["flag"],
                })

                output_rows.append(output_row)

            except Exception as error:

                print(
                    f"Warning: Row {row_number} needs review: {error}"
                )

                output_row = {
                    field: row.get(field, "")
                    for field in original_fields
                }

                # Use only valid category values
                output_row.update({
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        "The complaint could not be classified, "
                        "so it needs review."
                    ),
                    "flag": "NEEDS_REVIEW",
                })

                output_rows.append(output_row)

    # Write output CSV
    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(output_rows)

    print(
        f"Classification complete. "
        f"{len(output_rows)} rows written to {output_path}"
    )


def main():

    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for output CSV file",
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output
    )


if __name__ == "__main__":
    main()