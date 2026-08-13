"""
UC-0A — Complaint Classifier
Deterministic implementation based on agents.md and skills.md.
"""

import argparse
import csv
import re


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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

REQUIRED_FIELDS = {
    "complaint_id",
    "description",
}


def _text(row: dict) -> str:
    """Return normalized complaint description text."""
    return str(row.get("description") or "").strip()


def _contains(text: str, phrases) -> bool:
    """Return True when any phrase appears in text."""
    text = text.lower()
    return any(phrase.lower() in text for phrase in phrases)


def _find_trigger(text: str, phrases):
    """Return the first matching phrase."""
    lowered = text.lower()

    for phrase in phrases:
        if phrase.lower() in lowered:
            return phrase

    return None


def _classify_category(description: str):
    """
    Determine category from the complaint description.

    More specific infrastructure problems are checked before
    broad categories such as Other.
    """

    rules = [
        (
            "Pothole",
            [
                "pothole",
                "potholes",
            ],
        ),
        (
            "Drain Blockage",
            [
                "drain blocked",
                "blocked drain",
                "drain blockage",
                "drain clogged",
                "clogged drain",
            ],
        ),
        (
            "Flooding",
            [
                "flooded",
                "flooding",
                "flood",
                "waterlogged",
                "water logging",
                "waterlogging",
                "knee-deep",
                "knee deep",
                "stranded",
                "inaccessible",
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
                "flickering",
                "sparking",
            ],
        ),
        (
            "Waste",
            [
                "garbage",
                "garbage bins",
                "waste",
                "bulk waste",
                "dumped",
                "dead animal",
                "animal not removed",
                "rubbish",
            ],
        ),
        (
            "Noise",
            [
                "music past midnight",
                "loud music",
                "noise",
                "playing music",
                "sound pollution",
            ],
        ),
        (
            "Heritage Damage",
            [
                "heritage",
                "historic building",
                "historical building",
                "heritage street",
                "heritage structure",
            ],
        ),
        (
            "Heat Hazard",
            [
                "heat wave",
                "heatwave",
                "extreme heat",
                "heat hazard",
            ],
        ),
        (
            "Road Damage",
            [
                "road surface",
                "road damaged",
                "road damage",
                "road cracked",
                "road crack",
                "sinking road",
                "road sinking",
                "manhole",
                "manhole cover",
                "footpath",
                "footpath tiles",
                "broken pavement",
                "pavement",
                "upturned tiles",
            ],
        ),
    ]

    matches = []

    for category, phrases in rules:
        trigger = _find_trigger(description, phrases)

        if trigger:
            matches.append((category, trigger))

    # Resolve specific combinations deterministically.
    if _contains(
        description,
        ["manhole", "manhole cover", "footpath", "footpath tiles",
         "broken pavement", "pavement", "upturned tiles"]
    ):
        trigger = _find_trigger(
            description,
            [
                "manhole cover",
                "manhole",
                "footpath tiles",
                "footpath",
                "upturned tiles",
                "broken pavement",
                "pavement",
            ],
        )
        return "Road Damage", trigger

    # If both flooding and drain blockage are present, use Drain Blockage
    # when the blocked drain is explicitly the cause.
    if _contains(description, ["drain blocked", "blocked drain", "drain blockage"]):
        if _contains(description, ["flooded", "flooding", "waterlogged"]):
            trigger = _find_trigger(
                description,
                ["drain blocked", "blocked drain", "drain blockage"],
            )
            return "Drain Blockage", trigger

    if matches:
        return matches[0]

    return "Other", None


def _classify_priority(description: str):
    """
    Determine priority independently from category.
    """

    urgent_phrases = [
        "injury",
        "injured",
        "child",
        "children",
        "school",
        "school children",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse",
        "collapsed",
        "stranded",
        "inaccessible",
        "serious injury",
        "risk of serious injury",
        "electrical hazard",
        "sparking",
        "knee-deep",
        "knee deep",
    ]

    trigger = _find_trigger(description, urgent_phrases)

    if trigger:
        return "Urgent", trigger

    low_phrases = [
        "minor",
        "cosmetic",
        "appearance only",
    ]

    trigger = _find_trigger(description, low_phrases)

    if trigger:
        return "Low", trigger

    return "Standard", None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = str(row.get("complaint_id") or "").strip()
    description = _text(row)

    # Safe handling of invalid rows.
    if not complaint_id or not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": (
                "The complaint is missing a required complaint_id or "
                "description, so it cannot be classified reliably."
            ),
            "flag": "NEEDS_REVIEW",
        }

    category, category_trigger = _classify_category(description)
    priority, priority_trigger = _classify_priority(description)

    # Determine whether category is genuinely ambiguous.
    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Build an evidence-based reason.
    if category == "Other":
        reason = (
            f'The description does not provide a clear match to an allowed '
            f'category; the text begins with "{description[:80]}".'
        )
    elif priority_trigger:
        reason = (
            f'The complaint describes "{category_trigger}" and contains '
            f'"{priority_trigger}", so it is classified as {category} and '
            f'{priority}.'
        )
    else:
        reason = (
            f'The description contains "{category_trigger}", supporting '
            f'the {category} category; no urgent safety trigger is present, '
            f'so priority is {priority}.'
        )

    # Final enforcement checks.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"
        flag = "NEEDS_REVIEW"

    if not reason.strip():
        reason = "Classification could not be explained from the complaint description."
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

    Invalid rows do not stop processing.
    """

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=output_fields,
            )

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as exc:
                    result = {
                        "complaint_id": str(row.get("complaint_id") or "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": (
                            "The row could not be classified because of an "
                            f"input processing error: {exc}"
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