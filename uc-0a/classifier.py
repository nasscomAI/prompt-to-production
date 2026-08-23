"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
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


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        dict with:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = row.get("description")

    # Handle missing or empty complaint descriptions.
    if description is None or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No complaint text was provided.",
            "flag": "NEEDS_REVIEW",
        }

    description = str(description).strip()
    text = description.lower()

    # Mandatory severity enforcement.
    matched_severity = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if keyword in text
    ]

    priority = "Urgent" if matched_severity else "Standard"

    # Category signals.
    category_keywords = {
        "Pothole": [
            "pothole",
        ],
        "Flooding": [
            "flood",
            "flooded",
            "flooding",
            "waterlogged",
            "water logging",
            "waterlogging",
        ],
        "Streetlight": [
            "streetlight",
            "street light",
            "streetlights",
            "street lights",
        ],
        "Waste": [
            "garbage",
            "waste",
            "rubbish",
            "trash",
            "dumped",
            "dumping",
            "dead animal",
        ],
        "Noise": [
            "noise",
            "loud music",
            "music",
            "sound",
        ],
        "Road Damage": [
            "road surface",
            "road damaged",
            "road damage",
            "cracked road",
            "cracked surface",
            "sinking",
            "broken road",
            "road crack",
            "footpath",
            "footpath tiles",
            "broken tiles",
            "upturned tiles",
        ],
        "Heritage Damage": [
            "heritage",
            "historic",
            "historical",
        ],
        "Heat Hazard": [
            "heat hazard",
            "extreme heat",
            "heat risk",
            "heat",
        ],
        "Drain Blockage": [
            "drain blocked",
            "blocked drain",
            "drain blockage",
            "drain clogged",
            "clogged drain",
            "drain obstruction",
        ],
    }

    category_matches = []

    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            category_matches.append(category)

    # No recognizable category.
    if not category_matches:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f'The complaint states "{description}".',
            "flag": "NEEDS_REVIEW",
        }

    # Genuine ambiguity.
    if len(category_matches) > 1:
        category = category_matches[0]
        flag = "NEEDS_REVIEW"
    else:
        category = category_matches[0]
        flag = ""

    # Evidence-based one-sentence reason.
    reason = (
        f'The complaint explicitly mentions "{description}" '
        f'and is best classified as {category}.'
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
    Read input CSV, classify each row independently,
    and write the results to an output CSV.
    """

    results = []

    try:
        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as infile:

            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header row.")

            for row in reader:
                try:
                    result = classify_complaint(row)

                except Exception as exc:
                    complaint_id = row.get("complaint_id", "")

                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": (
                            f"Unable to classify complaint row "
                            f"because processing failed: "
                            f"{type(exc).__name__}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                results.append(result)

    except (OSError, csv.Error, ValueError) as exc:
        results.append({
            "complaint_id": "",
            "category": "Other",
            "priority": "Low",
            "reason": (
                f"Input processing failed because of "
                f"{type(exc).__name__}."
            ),
            "flag": "NEEDS_REVIEW",
        })

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields
        )

        writer.writeheader()

        for result in results:

            # Final category validation.
            if result["category"] not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"

            # Final priority validation.
            if result["priority"] not in ALLOWED_PRIORITIES:
                result["priority"] = "Low"
                result["flag"] = "NEEDS_REVIEW"

            # Final flag validation.
            if result["flag"] not in ("", "NEEDS_REVIEW"):
                result["flag"] = "NEEDS_REVIEW"

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