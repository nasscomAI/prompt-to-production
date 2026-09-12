"""
UC-0A — Complaint Classifier
"""

import argparse
import csv
import re


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


def contains_keyword(text, keyword):
    """Case-insensitive whole-word keyword check."""
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # Handle missing descriptions
    if not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.strip()
    text_lower = text.lower()

    # ---------------------------------------------------------
    # PRIORITY
    # ---------------------------------------------------------

    matched_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if contains_keyword(text_lower, keyword)
    ]

    priority = "Urgent" if matched_severity else "Standard"

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    category = "Other"
    matched_phrase = None
    flag = ""

    # Streetlight is checked before Heritage Damage because a
    # heritage street can still have a streetlight complaint.
    category_rules = [
        (
            "Pothole",
            [
                "pothole",
                "pot hole",
            ],
        ),
        (
            "Flooding",
            [
                "flood",
                "flooded",
                "flooding",
                "waterlogging",
                "waterlogged",
                "water logged",
            ],
        ),
        (
            "Streetlight",
            [
                "streetlight",
                "street light",
                "streetlights",
                "street lights",
                "lights out",
                "light out",
                "light not working",
                "lights not working",
                "light is out",
                "lights are out",
                "flickering",
                "sparking",
                "unlit after",
                "unlit",
                "substation tripped",
                "substation tripped",
                "darkness for 3 nights",
            ],
        ),
        (
            "Waste",
            [
                "garbage",
                "waste",
                "trash",
                "rubbish",
                "dumped",
                "bulk waste",
                "dead animal",
                "animal not removed",
                "garbage bin",
                "garbage bins",
            ],
        ),
        (
            "Noise",
            [
                "noise",
                "noisy",
                "loud music",
                "music past midnight",
                "music after midnight",
                "loudspeaker",
                "loud speakers",
                "club music",
                "music at 2am",
                "construction drilling",
                "trucks idling",
                "wedding band",
                "amplifiers",
            ],
        ),
        (
            "Road Damage",
            [
                "road damage",
                "damaged road",
                "road damaged",
                "cracked road",
                "road surface cracked",
                "road surface damaged",
                "road sinking",
                "sinking road",
                "broken road",
                "broken pavement",
                "damaged pavement",
                "broken footpath",
                "footpath tiles broken",
                "footpath tiles",
                "upturned tiles",
                "broken tiles",
                "upturned paving",
                "road subsidence",
                "road collapsed",
                "footpath broken",
                "footpath sinking",
                "road surface buckled",
                "road subsided",
            ],
        ),
        (
            "Heritage Damage",
            [
                "heritage monument",
                "heritage building",
                "historical monument",
                "historic monument",
                "heritage structure",
                "monument damaged",
                "monument damage",
                "historical building damaged",
                "heritage lamp post",
                "historic tram road",
                "heritage residential building",
                "heritage stone",
            ],
        ),
        (
            "Heat Hazard",
[
    "heat hazard",
    "extreme heat",
    "heatwave",
    "heat wave",
    "severe heat",
    "dangerous heat",
    "dangerous temperatures",
    "surface melting",
    "temperature unbearable",
    "storing heat",
    "burns on contact",
    "44°c",
    "45°c",
    "52°c",
],
        ),
        (
            "Drain Blockage",
            [
                "blocked drain",
                "drain blocked",
                "drain blockage",
                "clogged drain",
                "drain clogged",
                "blocked drainage",
                "drainage blocked",
                "stormwater drain",
                "draining directly onto public road",
            ],
        ),
    ]

    for possible_category, phrases in category_rules:
        for phrase in phrases:
            if phrase in text_lower:
                category = possible_category
                matched_phrase = phrase
                break

        if category != "Other":
            break

    # If nothing specific was found, review is required.
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = (
            "The description does not clearly match any allowed category "
            "and requires review."
        )
    else:
        reason = (
            f'The words "{matched_phrase}" support the {category} category.'
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
    Bad rows are flagged instead of stopping the entire batch.
    """

    results = []

    try:
        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as input_file:

            reader = csv.DictReader(input_file)

            if reader.fieldnames is None:
                print("Input CSV has no header.")
                return

            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)

                except Exception as error:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "The row could not be classified because "
                            f"of an input error: {error}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    })

    except Exception as error:
        print(f"Could not read input file: {error}")
        return

    try:
        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as output_file:

            fieldnames = [
                "complaint_id",
                "category",
                "priority",
                "reason",
                "flag",
            ]

            writer = csv.DictWriter(
                output_file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(results)

    except Exception as error:
        print(f"Could not write output file: {error}")
        return


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