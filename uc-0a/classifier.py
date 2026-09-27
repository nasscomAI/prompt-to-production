"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
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

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole"],
    "Flooding": ["flood", "flooding", "waterlogged", "waterlogging"],
    "Streetlight": [
        "streetlight",
        "street light",
        "lamp post",
        "street lamp",
        "light pole",
    ],
    "Waste": [
        "garbage",
        "waste",
        "trash",
        "litter",
        "rubbish",
        "dump",
        "dumped",
    ],
    "Noise": [
        "noise",
        "noisy",
        "loud",
        "sound pollution",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road crack",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "historic",
        "historical",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "heat wave",
        "extreme heat",
    ],
    "Drain Blockage": [
        "drain",
        "drainage",
        "blocked drain",
        "drain blockage",
        "clogged drain",
        "sewer",
    ],
}


def normalize(text: str) -> str:
    """Normalize text for keyword matching."""
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def contains_keyword(text: str, keyword: str) -> bool:
    """Check whether a keyword or phrase occurs in the description."""
    if " " in keyword:
        return keyword in text

    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None


def get_description(row: dict) -> str:
    """Find the complaint description column."""
    possible_columns = [
        "description",
        "complaint",
        "complaint_description",
        "text",
    ]

    for column in possible_columns:
        if column in row and str(row[column]).strip():
            return str(row[column]).strip()

    # Fallback: use the first non-empty non-ID field.
    for key, value in row.items():
        if key.lower() not in {"id", "complaint_id"} and str(value).strip():
            return str(value).strip()

    return ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """
    complaint_id = (
        row.get("complaint_id")
        or row.get("id")
        or ""
    )

    description = get_description(row)
    text = normalize(description)

    # Find severity keywords.
    severity_matches = [
        keyword
        for keyword in SEVERITY_KEYWORDS
        if contains_keyword(text, keyword)
    ]

    # Find category matches.
    category_matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [
            keyword
            for keyword in keywords
            if contains_keyword(text, keyword)
        ]

        if matched:
            category_matches.append((category, matched))

    # Genuinely ambiguous or unrecognized complaint.
    if len(category_matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_keywords = []
    elif len(category_matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_keywords = []
    else:
        category = category_matches[0][0]
        matched_keywords = category_matches[0][1]
        flag = ""

    # Enforcement rule:
    # Any severity keyword MUST make priority Urgent.
    if severity_matches:
        priority = "Urgent"
        cited_word = severity_matches[0]
        reason = (
            f'The description contains the specific word "{cited_word}", '
            f'which requires Urgent priority.'
        )
    elif matched_keywords:
        cited_word = matched_keywords[0]
        reason = (
            f'The description contains the specific word "{cited_word}", '
            f'supporting the {category} category.'
        )
        priority = "Standard"
    else:
        # Ambiguous complaints must not receive false confidence.
        excerpt = description.strip()

        if excerpt:
            words = excerpt.split()
            excerpt = " ".join(words[:8])
            reason = (
                f'The description states "{excerpt}", '
                f'but the category is genuinely ambiguous.'
            )
        else:
            reason = (
                "The complaint description is missing, "
                "so the category is genuinely ambiguous."
            )

        priority = "Standard"

    # Final validation of allowed values.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    if flag not in ("", "NEEDS_REVIEW"):
        flag = "NEEDS_REVIEW"

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

    Bad rows do not stop the complete batch. An error is recorded
    using Other + NEEDS_REVIEW so an output row is still produced.
    """
    try:
        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as infile:
            reader = csv.DictReader(infile)

            if not reader.fieldnames:
                raise ValueError("Input CSV has no header.")

            rows = list(reader)
            fieldnames = list(reader.fieldnames)

    except Exception as error:
        # Create an output file even when the input cannot be read.
        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=[
                    "complaint_id",
                    "category",
                    "priority",
                    "reason",
                    "flag",
                ],
            )
            writer.writeheader()
            writer.writerow({
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Input could not be processed: {error}.",
                "flag": "NEEDS_REVIEW",
            })

        return

    output_fields = list(fieldnames)

    for field in [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]:
        if field not in output_fields:
            output_fields.append(field)

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
                row.update(result)

            except Exception as error:
                # Do not crash on an individual bad row.
                row.update({
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        f"Unable to classify this row because of "
                        f"the input error: {error}."
                    ),
                    "flag": "NEEDS_REVIEW",
                })

            writer.writerow(row)


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