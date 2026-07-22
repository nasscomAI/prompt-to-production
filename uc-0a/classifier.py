"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and flag.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "road hole", "road damage", "tyre damage", "sinking"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "water logging", "knee-deep", "inaccessible"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "dark at night", "sparking", "substation", "wiring theft", "unlit", "darkness"],
    "Waste": ["garbage", "waste", "overflowing", "dead animal", "dumped", "bins", "renovation debris"],
    "Noise": ["music", "noise", "loud", "midnight", "disturbance", "amplifiers", "audible"],
    "Road Damage": ["cracked", "sinking", "broken tiles", "upturned", "footpath", "manhole", "missing cover", "cobblestones", "buckled", "subsided", "broken bench", "paving"],
    "Heritage Damage": ["heritage", "heritage street", "old city", "historical"],
    "Heat Hazard": ["heat", "extreme heat", "heatwave", "sunstroke", "melting", "temperatures", "°c", "burns on contact", "unbearable"],
    "Drain Blockage": ["drain blocked", "drainage blocked", "clogged drain", "sewer", "draining directly"],
}

AMBIGUOUS_PAIRS = [
    ({"Pothole", "Road Damage"}, "complaint mentions road issues that could be pothole or general road damage"),
    ({"Flooding", "Drain Blockage"}, "complaint mentions waterlogging and drain issues"),
    ({"Heritage Damage", "Streetlight"}, "complaint mentions heritage area with lighting issues"),
    ({"Waste", "Drain Blockage"}, "complaint mentions waste and drainage together"),
]


def _check_severity(description: str) -> bool:
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in SEVERITY_KEYWORDS)


def _find_categories(description: str) -> list:
    desc_lower = description.lower()
    matches = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matches.append(cat)
                break
    return matches


def _build_reason(description: str, category: str) -> str:
    desc_lower = description.lower()
    cat_keywords = CATEGORY_KEYWORDS.get(category, [])
    for kw in cat_keywords:
        if kw in desc_lower:
            idx = desc_lower.index(kw)
            start = max(0, idx - 40)
            end = min(len(description), idx + len(kw) + 40)
            snippet = description[start:end].strip()
            return f"Classified as {category} based on: \"{snippet}\""
    return f"Classified as {category} based on description content."


def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").strip()

    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or missing.",
            "flag": "NEEDS_REVIEW"
        }

    matched = _find_categories(desc)

    if not matched:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched) == 1:
        category = matched[0]
        flag = ""
    else:
        for pair, _ in AMBIGUOUS_PAIRS:
            if set(matched) == pair:
                flag = "NEEDS_REVIEW"
                break
        else:
            flag = ""
        category = matched[0]

    priority = "Urgent" if _check_severity(desc) else "Standard"
    reason = _build_reason(desc, category)

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "description" not in reader.fieldnames:
            raise ValueError(
                f"Input CSV has no 'description' column. Available: {reader.fieldnames}"
            )
        rows = list(reader)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append({**row, **result})
        except Exception as e:
            results.append({
                **row,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW"
            })

    if results:
        fieldnames = list(results[0].keys())
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
