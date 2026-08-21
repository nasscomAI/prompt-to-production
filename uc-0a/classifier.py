"""
UC-0A — Complaint Classifier
Implements the UC-0A schema with a controlled keyword-driven classifier and safe CSV processing.
"""
import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List

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

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "potholes"]),
    (
        "Drain Blockage",
        ["drain blocked", "blocked drain", "drain blockage", "clogged drain"],
    ),
    (
        "Flooding",
        [
            "flooded",
            "floods",
            "flood",
            "knee-deep",
            "standing water",
            "waterlogged",
            "inundat",
        ],
    ),
    (
        "Streetlight",
        [
            "streetlight",
            "streetlights",
            "lights out",
            "dark at night",
            "flickering",
            "sparking",
        ],
    ),
    (
        "Heritage Damage",
        ["heritage", "heritage street", "historical", "old city"],
    ),
    (
        "Heat Hazard",
        ["heat wave", "hot weather", "high temperature", "heat hazard"],
    ),
    ("Noise", ["music", "noise", "loud", "past midnight", "after midnight"]),
    (
        "Waste",
        [
            "garbage",
            "trash",
            "waste",
            "rubbish",
            "dumped",
            "overflowing bins",
            "dead animal",
            "health concern",
        ],
    ),
    (
        "Road Damage",
        [
            "cracked",
            "sinking",
            "manhole cover missing",
            "upturned",
            "depression",
            "broken pavement",
            "footpath tiles",
        ],
    ),
]

LOW_PRIORITY_CATEGORIES = {"Noise", "Waste"}


def _normalize_text(value: str) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _find_matching_phrases(text: str, phrases: Iterable[str]) -> List[str]:
    return [phrase for phrase in phrases if phrase in text]


def infer_category(description: str) -> (str, List[str]):
    normalized = _normalize_text(description)
    if not normalized:
        return "Other", []

    for category, phrases in CATEGORY_KEYWORDS:
        matches = _find_matching_phrases(normalized, phrases)
        if matches:
            return category, matches

    return "Other", []


def infer_priority(description: str, category: str) -> str:
    normalized = _normalize_text(description)
    if any(keyword in normalized for keyword in SEVERITY_KEYWORDS):
        return "Urgent"
    if category in LOW_PRIORITY_CATEGORIES:
        return "Low"
    return "Standard"


def build_reason(description: str, category: str, matches: List[str]) -> str:
    if not description or not description.strip():
        return "Missing complaint description; classification is set to Other with NEEDS_REVIEW."

    if matches:
        phrase = matches[0]
        return f"Classified as {category} because the description mentions '{phrase}'."

    excerpt = description.strip().replace("\n", " ")
    if len(excerpt) > 120:
        excerpt = excerpt[:117].rstrip() + "..."
    return f"Marked as {category} because the description says '{excerpt}'."


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    description = row.get("description", "")
    category, matches = infer_category(description)
    priority = infer_priority(description, category)
    reason = build_reason(description, category, matches)
    flag = "" if category != "Other" and description.strip() else "NEEDS_REVIEW"

    if category == "Other" and description.strip():
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    with input_file.open("r", encoding="utf-8", newline="") as csv_in:
        reader = csv.DictReader(csv_in)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing a header row.")

        output_fieldnames = list(reader.fieldnames)
        for extra in ["category", "priority", "reason", "flag"]:
            if extra not in output_fieldnames:
                output_fieldnames.append(extra)

        with Path(output_path).open("w", encoding="utf-8", newline="") as csv_out:
            writer = csv.DictWriter(csv_out, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                if row is None:
                    continue
                try:
                    classification = classify_complaint(row)
                except Exception:
                    classification = {
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Failed to classify row due to unexpected input; written as Other.",
                        "flag": "NEEDS_REVIEW",
                    }

                output_row = {**row, **classification}
                writer.writerow(output_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
