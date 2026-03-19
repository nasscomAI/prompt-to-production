"""
UC-0A — Complaint Classifier
Rule-based classifier following RICE enforcement from agents.md.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "pot-hole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlog", "water-log", "submerge", "knee-deep", "knee deep", "stranded"],
    "Streetlight": ["streetlight", "street light", "street-light", "lights out", "light out", "flickering", "sparking", "dark at night"],
    "Waste": ["garbage", "waste", "rubbish", "trash", "dump", "overflowing", "dead animal", "smell", "litter", "bulk waste", "renovation dumped"],
    "Noise": ["noise", "loud", "music", "midnight", "decibel", "honking"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken", "upturned", "footpath", "manhole", "missing cover", "tiles broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sunstroke", "temperature"],
    "Drain Blockage": ["drain", "blocked drain", "clogged", "blockage"],
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    matched_categories = []
    matched_words = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_words.setdefault(cat, []).append(kw)

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    is_urgent = False
    triggering_keywords = []
    for kw in SEVERITY_KEYWORDS:
        pattern = re.compile(r'\b' + re.escape(kw), re.IGNORECASE)
        if pattern.search(description):
            is_urgent = True
            triggering_keywords.append(kw)

    if is_urgent:
        priority = "Urgent"
    elif row.get("days_open", ""):
        try:
            days = int(row["days_open"])
            priority = "Urgent" if days > 15 else "Standard"
        except (ValueError, TypeError):
            priority = "Standard"
    else:
        priority = "Standard"

    cited = matched_words.get(category, [])
    if triggering_keywords:
        reason = (
            f"Description mentions '{triggering_keywords[0]}' (severity keyword) "
            f"and '{cited[0]}' indicating {category}."
            if cited
            else f"Description mentions '{triggering_keywords[0]}' (severity keyword)."
        )
    elif cited:
        reason = f"Description mentions '{cited[0]}' indicating {category}."
    else:
        reason = "Description does not match any known category keywords."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    failed = 0

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as exc:
                failed += 1
                print(f"WARN: skipped row {row.get('complaint_id', '?')}: {exc}", file=sys.stderr)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed {len(results)} rows, {failed} failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
