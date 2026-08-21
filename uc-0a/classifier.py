"""UC-0A pothole complaint classifier.

This version handles natural-language descriptions, severity keywords, and CSV batch processing.
The output follows the project's rules for category, priority, location, and reason.
"""

import argparse
import csv
import re
from typing import Iterable

URGENT_KEYWORDS = [
    "injury",
    "injured",
    "accident",
    "school",
    "student",
    "students",
    "children",
    "child",
    "hospital",
    "ambulance",
    "danger",
    "dangerous",
    "unsafe",
    "blockage",
    "blocked",
    "hazard",
    "collapse",
    "crash",
    "fell",
    "fall",
    "risk",
    "fire",
]

HIGH_KEYWORDS = [
    "large",
    "big",
    "deep",
    "severe",
    "major",
    "wide",
    "massive",
    "enormous",
    "gaping",
    "crater",
    "traffic",
    "traffic jam",
    "jam",
    "road closed",
    "road closure",
    "blocking traffic",
    "affecting traffic",
]

NORMAL_FALLBACK_KEYWORDS = [
    "small",
    "minor",
    "pothole",
    "road",
    "surface",
    "rough",
]


def _match_exact_phrase(description: str, phrase: str) -> str:
    """Return the exact matching substring from the description, preserving case."""
    if not description:
        return ""
    pattern = re.compile(r"(?i)\b" + re.escape(phrase.strip()) + r"\b")
    match = pattern.search(description)
    if match:
        return match.group(0)
    return ""


def _find_supporting_phrase(description: str, keywords: Iterable[str]) -> str:
    """Find the first exact phrase from the description that matches a keyword."""
    if not description:
        return ""

    text = description.strip()
    for keyword in keywords:
        phrase = _match_exact_phrase(text, keyword)
        if phrase:
            return phrase

    # Handle multi-word phrases explicitly.
    for phrase in ["affecting traffic", "traffic jam", "road closed", "road closure", "blocking traffic"]:
        if phrase.lower() in text.lower():
            return phrase

    return ""


def classify_pothole_report(location: str, description: str) -> dict:
    """Classify a single pothole report into category, location, priority, and reason."""
    location_value = (location or "").strip()
    description_value = (description or "").strip()

    urgent_phrase = _find_supporting_phrase(description_value, URGENT_KEYWORDS)
    if urgent_phrase:
        priority = "Urgent"
        reason = urgent_phrase
    else:
        high_phrase = _find_supporting_phrase(description_value, HIGH_KEYWORDS)
        if high_phrase:
            priority = "High"
            reason = high_phrase
        else:
            priority = "Normal"
            reason = _find_supporting_phrase(description_value, NORMAL_FALLBACK_KEYWORDS)
            if not reason:
                reason = "pothole" if "pothole" in description_value.lower() else description_value.split()[0] if description_value else ""

    return {
        "Category": "Pothole",
        "Location": location_value,
        "Priority": priority,
        "Reason": reason,
    }


def classify_complaint(row: dict) -> dict:
    """Compatibility wrapper for complaint rows in different CSV column layouts."""
    location = (
        row.get("location")
        or row.get("Location")
        or row.get("address")
        or row.get("Address")
        or row.get("street")
        or row.get("Street")
        or ""
    )
    description = (
        row.get("description")
        or row.get("Description")
        or row.get("details")
        or row.get("Details")
        or row.get("issue")
        or row.get("Issue")
        or ""
    )
    return classify_pothole_report(location, description)


def batch_classify(input_path: str, output_path: str):
    """Read CSV input, classify every row, and write the result CSV."""
    rows = []
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for raw_row in reader:
            rows.append(classify_complaint(raw_row))

    fieldnames = ["Category", "Location", "Priority", "Reason"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to the input CSV file")
    parser.add_argument("--output", required=True, help="Path to the output CSV file")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
