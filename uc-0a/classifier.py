"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path
from typing import List, Optional, Tuple

DATA_FILES_DIR = Path(__file__).resolve().parent.parent / "data" / "city-test-files"

ALLOWED_CATEGORIES: List[str] = [
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

SEVERITY_KEYWORDS: List[str] = [
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
    "Heritage Damage": ["heritage", "monument", "historical", "old city", "heritage street"],
    "Streetlight": ["streetlight", "street light", "lights out", "dark at night", "light out", "flickering", "sparking", "dark street"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drain blockage", "drain is blocked", "drainage blocked", "gutter blocked"],
    "Flooding": ["flood", "flooded", "waterlogged", "inundated", "knee-deep", "flooding", "stranded in water"],
    "Heat Hazard": ["heat hazard", "heatwave", "hot pavement", "hot", "temperature", "sunny"],
    "Noise": ["noise", "music", "loud", "sound", "speakers", "late night", "midnight", "car horns"],
    "Waste": ["garbage", "waste", "trash", "dumped", "bin", "bins", "dumping", "dead animal", "refuse", "smell"],
    "Pothole": ["pothole", "potholes"],
    "Road Damage": ["crack", "cracked", "sinking", "broken road", "upturned", "manhole cover missing", "road surface", "collapsed", "depression", "sinkhole"],
}

LOW_PRIORITY_CATEGORIES: List[str] = ["Noise", "Heritage Damage"]
PREFERRED_CATEGORY_ORDER: List[str] = [
    "Heritage Damage",
    "Streetlight",
    "Drain Blockage",
    "Flooding",
    "Heat Hazard",
    "Noise",
    "Waste",
    "Pothole",
    "Road Damage",
]


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


def _find_matching_category(description: str) -> Tuple[str, List[str], bool]:
    """Return the chosen category, matched keywords, and an ambiguity flag."""
    description_lower = description.lower()
    matched: dict = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                matched[category] = matched.get(category, []) + [keyword]
                break

    if not matched:
        return "Other", [], True

    if len(matched) == 1:
        category = next(iter(matched))
        return category, matched[category], False

    for category in PREFERRED_CATEGORY_ORDER:
        if category in matched:
            return category, matched[category], True

    chosen_category = next(iter(matched))
    return chosen_category, matched[chosen_category], True


def _compute_priority(description: str, category: str) -> str:
    """Urgent if any severity keyword is present, otherwise low or standard by category."""
    description_lower = description.lower()
    if any(keyword in description_lower for keyword in SEVERITY_KEYWORDS):
        return "Urgent"
    if category in LOW_PRIORITY_CATEGORIES:
        return "Low"
    return "Standard"


def _build_reason(description: str, matched_terms: List[str]) -> str:
    """Build a one-sentence reason that cites words found in the description."""
    description_lower = description.lower()
    if not description_lower:
        return "Missing description; unable to derive classification reason."

    if matched_terms:
        unique_terms = []
        for term in matched_terms:
            if term not in unique_terms:
                unique_terms.append(term)
        quoted_terms = ", ".join(f"'{term}'" for term in unique_terms[:3])
        return f"Description contains {quoted_terms}."

    severity_matches = [keyword for keyword in SEVERITY_KEYWORDS if keyword in description_lower]
    if severity_matches:
        quoted_terms = ", ".join(f"'{term}'" for term in severity_matches[:3])
        return f"Description contains {quoted_terms}."

    first_phrase = description_lower.replace("\n", " ").strip()
    if first_phrase:
        snippet = first_phrase[:100].rstrip()
        return f"Description includes '{snippet}'."

    return "Complaint description is present but no category keywords were found."


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row and return the output fields."""
    complaint_id = _normalize_text(row.get("complaint_id", ""))
    description = _normalize_text(row.get("description", ""))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description; insufficient information to classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_terms, ambiguous = _find_matching_category(description)
    flag = "NEEDS_REVIEW" if ambiguous or category == "Other" else ""
    priority = _compute_priority(description, category)
    reason = _build_reason(description, matched_terms)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read the input CSV, classify each row, and write the output CSV."""
    output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, mode="r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        rows = list(reader)

    with open(output_path, mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": _normalize_text(row.get("complaint_id", "")),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Failed to classify record due to invalid row data.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument(
        "--input",
        default=None,
        help="Path to an input CSV, typically under ../data/city-test-files/test_[city].csv",
    )
    parser.add_argument(
        "--city",
        default=None,
        help="City name to build the input path from data/city-test-files when --input is omitted.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to write results CSV. If omitted with --city, defaults to results_[city].csv.",
    )
    args = parser.parse_args()

    if args.input is None:
        if args.city is None:
            parser.error("Either --input or --city must be provided.")
        args.input = str(DATA_FILES_DIR / f"test_{args.city}.csv")

    if args.output is None:
        if args.city is None:
            parser.error("--output is required when --city is not provided.")
        args.output = f"results_{args.city}.csv"

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
