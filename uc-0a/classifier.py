"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed",
]

CATEGORY_RULES = [
    ("Pothole",         ["pothole", "pot hole"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat", "sun", "temperature"]),
    ("Streetlight",     ["streetlight", "street light", "light out", "lights out", "lamp", "lighting"]),
    ("Drain Blockage",  ["drain", "drainage", "sewage", "sewer", "manhole", "blocked drain", "blockage"]),
    ("Flooding",        ["flood", "flooded", "waterlogged", "submerged", "standing water", "water logging"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "bin", "dumping", "litter", "debris",
                         "dead animal", "smell", "overflowing", "health concern"]),
    ("Noise",           ["noise", "music", "loud", "honking"]),
    ("Road Damage",     ["road surface", "road damage", "cracked", "sinking", "broken", "footpath",
                         "road deteriorated"]),
]


def _find_matches(desc_lower: str) -> list[str]:
    matches = []
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matches.append(cat)
                break
    return matches


def _categorize(desc_lower: str) -> str:
    matches = _find_matches(desc_lower)
    if not matches:
        return "Other"
    return matches[0]


def _is_ambiguous(desc_lower: str, chosen: str) -> bool:
    matches = _find_matches(desc_lower)
    return len(matches) > 1


def _determine_priority(desc_lower: str) -> str:
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _build_reason(category: str, description: str) -> str:
    desc_lower = description.lower()
    for cat, keywords in CATEGORY_RULES:
        if cat == category:
            for kw in keywords:
                if kw in desc_lower:
                    idx = desc_lower.index(kw)
                    start = max(0, idx)
                    end = min(len(description), idx + 80)
                    snippet = description[start:end].strip()
                    return f"Description mentions '{kw}' — classified as {category}"
    if category == "Other":
        return f"No category keywords found in description — classified as Other"
    return f"Classified as {category} based on description"


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category = _categorize(desc_lower)
    ambiguous = _is_ambiguous(desc_lower, category) if category != "Other" else False
    priority = _determine_priority(desc_lower)
    reason = _build_reason(category, description)
    flag = "NEEDS_REVIEW" if (ambiguous or category == "Other") else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "description" not in reader.fieldnames:
            print(f"Error: input CSV missing 'description' column. Found: {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)
        for row in reader:
            rows.append(row)

    out_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in rows:
            result = classify_complaint(row)
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
