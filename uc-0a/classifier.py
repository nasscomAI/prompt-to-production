"""
UC-0A — Complaint Classifier
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
    "Pothole": [
        "pothole",
        "pot hole",
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
        "lamp post",
        "lamp",
        "light pole",
        "lights are out",
        "light is out",
    ],
    "Waste": [
        "garbage",
        "waste",
        "trash",
        "rubbish",
        "litter",
        "dump",
        "dumped",
        "garbage collection",
    ],
    "Noise": [
        "noise",
        "noisy",
        "loud",
        "loudspeaker",
        "sound pollution",
    ],
    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "road is broken",
        "cracked road",
        "road crack",
        "road surface",
        "road has deteriorated",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "historic building",
        "historical building",
        "historical site",
        "heritage site",
    ],
    "Heat Hazard": [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
        "hot pavement",
        "heat risk",
    ],
    "Drain Blockage": [
        "drain",
        "drainage",
        "blocked drain",
        "drain blockage",
        "clogged drain",
        "blocked drainage",
        "sewer blockage",
    ],
}


def find_matching_keyword(text: str, keywords: list[str]) -> str | None:
    """Return the first keyword that appears in the complaint."""
    text_lower = text.lower()

    for keyword in keywords:
        if keyword.lower() in text_lower:
            return keyword

    return None


def contains_severity_keyword(text: str) -> str | None:
    """Return the severity keyword that triggered Urgent, if any."""
    text_lower = text.lower()

    for keyword in SEVERITY_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, text_lower):
            return keyword

    return None


def classify_category(description: str) -> tuple[str, str | None]:
    """
    Determine category from the fixed taxonomy.

    Returns:
        (category, matched_keyword)
    """

    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = find_matching_keyword(description, keywords)

        if matched:
            matches.append((category, matched))

    # No category can be determined.
    if not matches:
        return "Other", None

    # More than one category matches: avoid false confidence.
    if len(matches) > 1:
        return "Other", None

    category, matched_keyword = matches[0]

    if category not in ALLOWED_CATEGORIES:
        return "Other", None

    return category, matched_keyword


def classify_priority(description: str) -> tuple[str, str | None]:
    """
    Assign priority.

    Any required severity keyword makes the complaint Urgent.
    Otherwise use Standard for a specific complaint and Low only when
    the complaint describes a minor/non-urgent issue.
    """

    severity_keyword = contains_severity_keyword(description)

    if severity_keyword:
        return "Urgent", severity_keyword

    return "Standard", None


def build_reason(
    description: str,
    category: str,
    category_keyword: str | None,
    severity_keyword: str | None,
    ambiguous: bool,
) -> str:
    """Create a one-sentence reason citing words from the complaint."""

    if not description.strip():
        return (
            "The complaint description is missing, so the category cannot be determined."
        )

    if ambiguous and severity_keyword:
        return (
            f"The description mentions '{severity_keyword}', which triggers "
            f"Urgent priority; the category is ambiguous."
        )

    if ambiguous:
        return (
            "The description does not provide enough specific information "
            "to determine one category confidently."
        )

    if severity_keyword and category_keyword:
        return (
            f"The description mentions '{category_keyword}' and '{severity_keyword}', "
            f"supporting {category} classification and triggering Urgent priority."
        )

    if severity_keyword:
        return (
            f"The description mentions '{severity_keyword}', which triggers "
            f"Urgent priority under the severity rules."
        )

    if category_keyword:
        return (
            f"The description mentions '{category_keyword}', which supports "
            f"the {category} category."
        )

    return f"The description supports the {category} category."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = str(
        row.get("complaint_id")
        or row.get("id")
        or ""
    ).strip()

    # Support common description column names.
    description = str(
        row.get("description")
        or row.get("complaint")
        or row.get("complaint_description")
        or row.get("text")
        or ""
    ).strip()

    # Missing description should not crash the batch.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing, so the category cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_keyword = classify_category(description)

    priority, severity_keyword = classify_priority(description)

    ambiguous = category == "Other"

    reason = build_reason(
        description=description,
        category=category,
        category_keyword=category_keyword,
        severity_keyword=severity_keyword,
        ambiguous=ambiguous,
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every row, and write the results CSV.

    Bad individual rows are converted to NEEDS_REVIEW instead of
    stopping the complete batch.
    """

    results = []

    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header row.")

            for row_number, row in enumerate(reader, start=2):
                try:
                    result = classify_complaint(row)
                    results.append(result)

                except Exception as exc:
                    complaint_id = str(row.get("complaint_id", "")).strip()

                    results.append(
                        {
                            "complaint_id": complaint_id,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Row {row_number} could not be classified safely: {exc}.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )

    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    except csv.Error as exc:
        raise ValueError(f"Could not read CSV file: {exc}")

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields,
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