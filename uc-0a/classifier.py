"""
UC-0A — Complaint Classifier
Complaint classification using the fixed UC-0A taxonomy.
"""

import argparse
import csv


# ---------------------------------------------------------
# UC-0A allowed classification values
# ---------------------------------------------------------

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

ALLOWED_PRIORITIES = [
    "Urgent",
    "Standard",
    "Low",
]

# These words must always trigger Urgent
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


# ---------------------------------------------------------
# Classify one complaint
# ---------------------------------------------------------

def classify_complaint(row: dict) -> dict:

    complaint_id = row.get("complaint_id", "")

    description = (
        row.get("description")
        or row.get("complaint")
        or row.get("complaint_description")
        or ""
    ).strip()

    # Missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # -----------------------------------------------------
    # Priority detection
    # -----------------------------------------------------

    matched_severity = None

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            matched_severity = keyword
            break

    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # -----------------------------------------------------
    # Category keyword map
    # -----------------------------------------------------

    keyword_map = {

        "Pothole": [
            "pothole",
            "potholes",
        ],

        "Flooding": [
            "flood",
            "flooding",
            "waterlogged",
            "water logging",
            "waterlogging",
        ],

        "Streetlight": [
            "streetlight",
            "street light",
            "street lamp",
            "lamp post",
        ],

        "Waste": [
            "garbage",
            "waste",
            "trash",
            "rubbish",
            "litter",
            "dead animal",
            "animal not removed",
        ],

        "Noise": [
            "noise",
            "loud music",
            "loudspeaker",
            "loud speaker",
            "music",
            "playing music",
            "sound",
        ],

        "Road Damage": [
            "road damage",
            "damaged road",
            "broken road",
            "cracked road",
            "road crack",
            "road surface",
            "sinking road",
            "footpath",
            "footpath tiles",
            "broken pavement",
            "upturned",
        ],

        "Heritage Damage": [
            "heritage",
            "monument",
            "historic building",
            "historical building",
        ],

        "Heat Hazard": [
            "heat",
            "extreme heat",
            "heatwave",
            "heat wave",
        ],

        "Drain Blockage": [
            "drain",
            "drainage",
            "blocked drain",
            "drain blockage",
            "sewer",
        ],
    }

    # -----------------------------------------------------
    # Find matching categories
    # -----------------------------------------------------

    matches = []

    for category, keywords in keyword_map.items():

        for keyword in keywords:

            if keyword in text:

                matches.append(
                    (category, keyword)
                )

                break

    # Remove duplicate categories
    unique_categories = []

    for category, keyword in matches:

        if category not in unique_categories:
            unique_categories.append(category)

    # -----------------------------------------------------
    # No category found
    # -----------------------------------------------------

    if len(unique_categories) == 0:

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f'No allowed category was clearly identified '
                f'from the description "{description}".'
            ),
            "flag": "NEEDS_REVIEW",
        }

    # -----------------------------------------------------
    # Multiple categories found
    # -----------------------------------------------------

    if len(unique_categories) > 1:

        matched_words = ", ".join(
            f'"{keyword}"'
            for category, keyword in matches
        )

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f'The description contains multiple possible '
                f'category indicators: {matched_words}.'
            ),
            "flag": "NEEDS_REVIEW",
        }

    # -----------------------------------------------------
    # Single category found
    # -----------------------------------------------------

    category, keyword = matches[0]

    reason = (
        f'The description contains the specific indicator '
        f'"{keyword}", which supports the {category} category.'
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


# ---------------------------------------------------------
# Batch classification
# ---------------------------------------------------------

def batch_classify(input_path: str, output_path: str):

    results = []

    try:

        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as infile:

            reader = csv.DictReader(infile)

            if not reader.fieldnames:
                raise ValueError(
                    "Input CSV has no header."
                )

            for row in reader:

                try:

                    result = classify_complaint(row)

                    results.append(result)

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
                            f"Row could not be classified "
                            f"because of an input error: {error}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    })

    except FileNotFoundError:

        print(
            f"Input file not found: {input_path}"
        )

        return

    except Exception as error:

        print(
            f"Could not read input CSV: {error}"
        )

        return

    # -----------------------------------------------------
    # Write output CSV
    # -----------------------------------------------------

    try:

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

    except Exception as error:

        print(
            f"Could not write output CSV: {error}"
        )


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

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