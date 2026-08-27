"""UC-0A citizen-complaint classifier.

The rules in this module implement the operating contract in ``agents.md``:
classifications are based only on the row description and use the fixed
taxonomy required by the project.
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_CATEGORIES = (
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
)
URGENT_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

# More specific categories are evaluated before broader road and water terms.
CATEGORY_PATTERNS = (
    ("Heritage Damage", r"\b(heritage|monument|historic(?:al)?|temple|statue|fort)\b"),
    ("Drain Blockage", r"\b(drain|drainage|gutter|sewer)\b[^.]{0,45}\b(block(?:ed|age)?|clog(?:ged)?|chok(?:ed)?|jam(?:med)?)\b|\b(block(?:ed|age)?|clog(?:ged)?|chok(?:ed)?|jam(?:med)?)\b[^.]{0,45}\b(drain|drainage|gutter|sewer)\b"),
    ("Flooding", r"\b(flood(?:ed|ing)?|water[ -]?log(?:ged|ging)?|inundat(?:ed|ion)|standing water)\b"),
    ("Pothole", r"\b(pothole|pot hole)s?\b"),
    ("Streetlight", r"\b(street ?lights?|lamp ?posts?|road ?lights?)\b"),
    ("Waste", r"\b(garbage|rubbish|trash|litter|waste|dumping|bin overflow)\b"),
    ("Noise", r"\b(noise|noisy|loud music|loudspeaker|sound pollution)\b"),
    ("Heat Hazard", r"\b(heat ?wave|extreme heat|heat hazard|heatstroke|overheating)\b"),
    ("Road Damage", r"\b(road|street|pavement|carriageway)\b[^.]{0,45}\b(damag(?:e|ed)|crack(?:ed|s)?|broken|collapse[ds]?)\b|\b(damag(?:e|ed)|crack(?:ed|s)?|broken|collapse[ds]?)\b[^.]{0,45}\b(road|street|pavement|carriageway)\b"),
)


def _description_from(row: dict[str, Any]) -> str:
    """Return a validated complaint description or raise ``ValueError``."""
    if not isinstance(row, dict):
        raise ValueError("complaint row must be a dictionary")
    description = row.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("description must be a non-empty string")
    return description.strip()


def _priority(description: str) -> str:
    """Apply the required severity-keyword escalation rule."""
    normalised = description.casefold()
    return "Urgent" if any(keyword in normalised for keyword in URGENT_KEYWORDS) else "Standard"


def _classify_category(description: str) -> tuple[str, str, str]:
    """Return category, supporting text, and review flag for a description."""
    for category, pattern in CATEGORY_PATTERNS:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            return category, match.group(0), ""

    # A short, exact excerpt keeps even review reasons tied to the source text.
    excerpt = " ".join(description.split()[:12])
    return "Other", excerpt, "NEEDS_REVIEW"


def classify_complaint(row: dict[str, Any]) -> dict[str, str]:
    """Classify one complaint into category, priority, reason, and flag.

    ``ValueError`` is raised for an invalid description. A valid but
    unclassifiable description is returned as ``Other`` with ``NEEDS_REVIEW``
    instead of being guessed.
    """
    description = _description_from(row)
    category, evidence, flag = _classify_category(description)
    if flag:
        reason = f"The description says '{evidence}', which does not establish a category."
    else:
        reason = f"The description says '{evidence}', indicating {category}."

    return {
        "complaint_id": str(row.get("complaint_id", "")),
        "category": category,
        "priority": _priority(description),
        "reason": reason,
        "flag": flag,
    }


def _invalid_result(row: dict[str, Any]) -> dict[str, str]:
    """Create a clearly flagged batch result when a row cannot be validated."""
    return {
        "complaint_id": str(row.get("complaint_id", "")),
        "category": "Other",
        "priority": "Standard",
        "reason": "No valid complaint description was supplied.",
        "flag": "NEEDS_REVIEW",
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Classify every CSV row and write results, reporting invalid rows.

    Row-level validation failures do not prevent valid rows from being written.
    File-level errors, including missing files or a missing ``description``
    column, are reported as ``ValueError`` before an output file is created.
    """
    with open(input_path, "r", encoding="utf-8-sig", newline="") as input_file:
        reader = csv.DictReader(input_file)
        if not reader.fieldnames or "description" not in reader.fieldnames:
            raise ValueError("input CSV must contain a description column")
        input_fields = list(reader.fieldnames)
        rows = list(reader)

    result_fields = ["category", "priority", "reason", "flag"]
    output_fields = input_fields + [field for field in result_fields if field not in input_fields]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        for row_number, row in enumerate(rows, start=2):
            try:
                result = classify_complaint(row)
            except ValueError as error:
                result = _invalid_result(row)
                print(f"Row {row_number}: {error}", file=sys.stderr)
            writer.writerow({**row, **result})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Done. Results written to {args.output}")
