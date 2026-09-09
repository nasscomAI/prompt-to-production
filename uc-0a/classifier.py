"""UC-0A — Complaint Classifier.

This file enforces the exact taxonomy rules from the UC-0A README and agent metadata:
- strict category schema
- Urgent priority for specified severity keywords
- one-sentence justification citing the original complaint text
- NEEDS_REVIEW when the category is genuinely ambiguous
"""

import argparse
import csv
import re
from pathlib import Path

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

CATEGORY_RULES = [
    ("Pothole", ["pothole", "potholes"]),
    ("Flooding", ["flood", "flooding", "flooded", "waterlogged", "knee-deep", "inundat"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "lamp", "flickering", "sparking", "dark at night"]),
    ("Waste", ["garbage", "waste", "overflowing bins", "overflowing garbage", "dumped", "dead animal", "refuse", "smell"]),
    ("Noise", ["noise", "music", "loud", "past midnight", "midnight", "sound"]),
    ("Road Damage", ["road surface", "cracked", "broken tiles", "upturned", "footpath", "sinking", "surface cracked", "missing manhole cover", "road damage"]),
    ("Heritage Damage", ["heritage", "monument", "historic", "heritage street"]),
    ("Heat Hazard", ["heat", "heatwave", "temperature", "sun", "hot weather"]),
    ("Drain Blockage", ["drain blocked", "drainage blocked", "blocked drain", "clogged drain", "drain blockage", "manhole cover missing"]),
]


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _normalize_keywords(text):
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def _citation_from_description(description):
    cleaned = _clean_text(description)
    if not cleaned:
        return 'The complaint description is empty.'

    normalized = _normalize_keywords(cleaned)
    phrases = [
        "pothole",
        "flooded",
        "school children",
        "school",
        "streetlight",
        "garbage",
        "music",
        "cracked",
        "heritage",
        "heat",
        "drain blocked",
        "fell",
        "injury",
        "hazard",
    ]

    for phrase in phrases:
        if phrase in normalized:
            idx = normalized.find(phrase)
            start = max(0, idx - 18)
            end = min(len(normalized), idx + len(phrase) + 18)
            snippet = cleaned[start:end]
            snippet = re.sub(r"\s+", " ", snippet).strip()
            if snippet:
                return f'The complaint cites "{snippet}" in the description.'

    # fallback to the first short clause in the description
    sentence = cleaned.split(".")[0].strip()
    if sentence:
        return f'The complaint cites "{sentence}" in the description.'
    return f'The complaint cites the reported issue in the description.'


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row using explicit schema enforcement and citations."""
    complaint_id = _clean_text(row.get("complaint_id"))
    description = _clean_text(row.get("description", ""))

    if not complaint_id:
        raise ValueError("Every complaint row must include a complaint_id.")

    if not description:
        raise ValueError(f"Complaint {complaint_id} is missing a description and cannot be classified.")

    normalized_description = _normalize_keywords(description)
    matched_categories = []
    for category, keywords in CATEGORY_RULES:
        if any(keyword in normalized_description for keyword in keywords):
            matched_categories.append(category)

    if not matched_categories:
        selected_category = "Other"
    else:
        selected_category = matched_categories[0]

    if len(matched_categories) > 1:
        ambiguous = True
    else:
        ambiguous = False

    priority = "Standard"
    if any(keyword in normalized_description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif selected_category == "Noise" and "music" in normalized_description:
        priority = "Low"

    flag = "NEEDS_REVIEW" if ambiguous else ""

    if selected_category not in ALLOWED_CATEGORIES:
        selected_category = "Other"

    reason = _citation_from_description(description)
    return {
        "complaint_id": complaint_id,
        "category": selected_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read the input CSV, classify each complaint row, and write a structured output CSV."""
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with input_file.open("r", newline="", encoding="utf-8-sig") as source_file:
        reader = csv.DictReader(source_file)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing a header row.")

        required_columns = {"complaint_id", "description"}
        missing_columns = sorted(required_columns - set(reader.fieldnames))
        if missing_columns:
            raise ValueError(
                "Input CSV is missing required fields: " + ", ".join(missing_columns)
            )

        output_rows = []
        for row_number, row in enumerate(reader, start=2):
            try:
                output_rows.append(classify_complaint(row))
            except ValueError as exc:
                output_rows.append(
                    {
                        "complaint_id": _clean_text(row.get("complaint_id")) or f"ROW_{row_number}",
                        "category": "Other",
                        "priority": "Low",
                        "reason": str(exc),
                        "flag": "NEEDS_REVIEW",
                    }
                )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with output_file.open("w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
