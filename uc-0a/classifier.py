"""UC-0A complaint classifier.

The classifier is deliberately keyword-based: each decision must be supported
by words in the complaint itself and by the fixed UC-0A taxonomy.
"""

import argparse
import csv
import re
from typing import Iterable, List


OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]
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
SEVERITY_KEYWORDS = (
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

CATEGORY_PATTERNS = (
    ("Heritage Damage", ("heritage", "historic", "old city")),
    ("Drain Blockage", ("drain blocked", "blocked drain", "drain blockage", "manhole")),
    ("Streetlight", ("streetlight", "streetlights", "street light", "lights out", "light flickering")),
    ("Flooding", ("flood", "floods", "flooded", "flooding", "waterlogging", "water logged")),
    ("Pothole", ("pothole",)),
    ("Waste", ("garbage", "waste", "dead animal", "dumped", "rubbish", "litter")),
    ("Noise", ("noise", "music", "loud", "sound")),
    ("Heat Hazard", ("heat", "hot surface", "heatwave")),
    ("Road Damage", ("road surface", "road damaged", "cracked", "broken", "upturned")),
)


def _contains_keyword(text: str, keyword: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", text, re.IGNORECASE) is not None


def _first_evidence(description: str, terms: Iterable[str]) -> str:
    for term in terms:
        match = re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", description, re.IGNORECASE)
        if match:
            return match.group(0)
    return ""


def classify_complaint(row: dict) -> dict:
    """Classify one row while always returning the fixed output shape."""
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    description_value = row.get("description") if isinstance(row, dict) else None
    description = description_value.strip() if isinstance(description_value, str) else ""
    priority = "Urgent" if any(
        _contains_keyword(description, keyword) for keyword in SEVERITY_KEYWORDS
    ) else "Standard"

    category = "Other"
    evidence = ""
    for candidate, terms in CATEGORY_PATTERNS:
        evidence = _first_evidence(description, terms)
        if evidence:
            category = candidate
            break

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "Description is missing, so the category cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    if not evidence:
        quoted_words = " ".join(description.split()[:3]).strip(".,;:!?")
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": 'The words "' + quoted_words + '" do not identify a supported category.',
            "flag": "NEEDS_REVIEW",
        }

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": 'The words "' + evidence + '" support the ' + category + " category.",
        "flag": "",
    }


def _fallback_row(row: object, index: int) -> dict:
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    if not complaint_id:
        complaint_id = "row-" + str(index)
    description = str(row.get("description", "")) if isinstance(row, dict) else ""
    priority = "Urgent" if any(
        _contains_keyword(description, keyword) for keyword in SEVERITY_KEYWORDS
    ) else "Standard"
    return {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": priority,
        "reason": "The input row is malformed, so the category cannot be determined.",
        "flag": "NEEDS_REVIEW",
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Classify every CSV row and write one valid output row per input row."""
    results: List[dict] = []
    with open(input_path, "r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        for index, row in enumerate(reader, start=1):
            try:
                results.append(classify_complaint(row))
            except (AttributeError, TypeError, ValueError, csv.Error):
                results.append(_fallback_row(row, index))

    with open(output_path, "w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to " + args.output)


if __name__ == "__main__":
    main()
