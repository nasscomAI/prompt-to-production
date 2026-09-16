"""
UC-0A — Complaint Classifier
Rule-based implementation guided by agents.md and skills.md.
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

ALLOWED_PRIORITIES = [
    "Urgent",
    "Standard",
    "Low",
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

CATEGORY_TERMS = {
    "Pothole": [
        "pothole",
    ],
    "Flooding": [
        "flood", "floods",
        "flooded",
        "flooding",
        "waterlogged",
        "water logging",
    ],
    "Streetlight": [
        "streetlight", "streetlights",
        "street light",
        "lights out",
        "light out",
    ],
    "Waste": [
        "garbage",
        "waste",
        "dumped",
        "dumping",
        "dead animal",
        "overflowing garbage bins",
        "overflowing bins",
        "waste bins",
    ],
    "Noise": [
        "noise",
        "music",
        "loud",
        "sound",
    ],
    "Road Damage": [
        "road surface",
        "road damage",
        "cracked road",
        "cracked",
        "sinking",
        "broken road",
        "tiles broken",
        "footpath",
        "manhole",
    ],
    "Heritage Damage": [
        "heritage",
        "historic",
        "historical",
    ],
    "Heat Hazard": [
        "heat",
        "extreme heat",
        "heatwave",
        "heat wave",
    ],
    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "drain blockage",
    ],
}


def _contains_keyword(text, keyword):
    """Case-insensitive whole-word match."""
    return re.search(
        rf"\b{re.escape(keyword)}\b",
        text,
        re.IGNORECASE,
    ) is not None


def _find_severity_keyword(text):
    """Return the first severity keyword found."""
    for keyword in SEVERITY_KEYWORDS:
        if _contains_keyword(text, keyword):
            return keyword
    return None


def _find_category_matches(description):
    """Return categories and evidence phrases supported by the description."""
    matches = []

    for category, terms in CATEGORY_TERMS.items():
        for term in terms:
            if _contains_keyword(description, term):
                matches.append((category, term))
                break

    return matches


def _classify_category(description):
    """
    Determine the best-supported category.

    Returns:
        category, evidence_phrase, ambiguous
    """

    matches = _find_category_matches(description)

    if not matches:
        return "Other", None, False

    categories = [item[0] for item in matches]

    # If flooding and a blocked drain are both mentioned,
    # classify the primary reported problem as Flooding.
    if "Flooding" in categories and "Drain Blockage" in categories:
        matches = [
            item
            for item in matches
            if item[0] != "Drain Blockage"
        ]

    categories = [item[0] for item in matches]

    # A streetlight problem in a heritage/old-city area is
    # still primarily a Streetlight complaint.
    if "Streetlight" in categories and "Heritage Damage" in categories:
        matches = [
            item
            for item in matches
            if item[0] != "Heritage Damage"
        ]

    category, evidence_phrase = matches[0]

    ambiguous = len(matches) > 1

    return category, evidence_phrase, ambiguous


def _make_reason(category, evidence_phrase, severity_keyword):
    """Create exactly one evidence-based sentence."""

    if category == "Other":

        if severity_keyword:
            return (
                'The description does not support an allowed specific '
                f'category but contains "{severity_keyword}", requiring urgent review.'
            )

        return (
            "The description does not contain evidence supporting any "
            "specific allowed category, so it is classified as Other."
        )

    if severity_keyword:
        return (
            f'The description contains "{evidence_phrase}" supporting '
            f'{category} and "{severity_keyword}" requiring urgent priority.'
        )

    return (
        f'The description contains "{evidence_phrase}" supporting '
        f'the {category} category.'
    )


def classify_complaint(row):
    """
    Classify a single complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Missing description: preserve the row and flag it.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, evidence_phrase, ambiguous = _classify_category(
        description
    )

    severity_keyword = _find_severity_keyword(description)

    # Any severity keyword makes the complaint Urgent.
    if severity_keyword:
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = _make_reason(
        category,
        evidence_phrase,
        severity_keyword,
    )

    flag = "NEEDS_REVIEW" if ambiguous else ""

    # Final schema validation.
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


def batch_classify(input_path, output_path):
    """
    Read input CSV, classify every row, and write results CSV.

    A bad row does not stop the entire batch.
    """

    results = []

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as infile:

        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        for row in reader:

            try:
                result = classify_complaint(row)

            except Exception as exc:
                result = {
                    "complaint_id": (
                        row.get("complaint_id") or ""
                    ).strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        f"Classification failed for this row: {str(exc)}."
                    ),
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
        newline="",
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
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
        help="Path to test_[city].csv",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV",
    )

    args = parser.parse_args()

    batch_classify(
        args.input,
        args.output,
    )

    print(f"Done. Results written to {args.output}")
