"""
UC-0A — Complaint Classifier.

Reads a single citizen complaint and assigns exactly one of ten fixed categories,
a priority, a one-sentence reason citing the description, and an optional ambiguity
flag, per the enforcement rules in agents.md and skills.md.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "deep hole", "hole in the road"],
    "Flooding": ["flood", "waterlog", "knee-deep", "standing water", "submerged", "inaccessible"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "lamp", "flicker", "sparking", "dark at night"],
    "Waste": ["garbage", "waste", "bin", "litter", "dump", "dead animal", "trash", "refuse", "odor", "smell"],
    "Noise": ["noise", "music", "loud", "honking", "horn", "past midnight", "late night"],
    "Road Damage": ["cracked", "sinking", "crack", "road surface", "pavement", "upturned", "uneven"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "hot weather", "temperature", "heatwave"],
    "Drain Blockage": ["drain", "blocked", "blockage", "sewer", "manhole", "clogged", "choked"],
}

CATEGORY_PRECEDENCE = [
    "Heritage Damage", "Heat Hazard", "Pothole", "Drain Blockage",
    "Flooding", "Streetlight", "Road Damage", "Waste", "Noise",
]


def _description_of(row: dict) -> str:
    for key, value in row.items():
        if str(key).strip().lower() == "description":
            return (value or "").strip()
    return ""


def _matched_keywords(description: str, keywords) -> list:
    lowered = description.lower()
    return [kw for kw in keywords if kw in lowered]


def _classify_priority(description: str) -> str:
    lowered = description.lower()
    if any(kw in lowered for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _reason_for(description: str, category: str, keywords: list) -> str:
    quoted = ", ".join('"{0}"'.format(kw) for kw in keywords[:3])
    return 'Description contains {0}, which fits {1}.'.format(quoted, category)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns a dict with exactly the keys: category, priority, reason, flag.
    """
    description = _description_of(row)
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": ("No description provided; category cannot be "
                       "determined from the input row."),
            "flag": "NEEDS_REVIEW",
        }

    matched = {}
    for category in CATEGORIES:
        if category == "Other":
            continue
        keywords = _matched_keywords(description, CATEGORY_KEYWORDS[category])
        if keywords:
            matched[category] = keywords

    priority = _classify_priority(description)

    if not matched:
        return {
            "category": "Other",
            "priority": priority,
            "reason": ("Description matches none of the allowed categories; "
                       "cannot be determined from the description alone."),
            "flag": "NEEDS_REVIEW",
        }

    best_score = max(len(kws) for kws in matched.values())
    top = [c for c, kws in matched.items() if len(kws) == best_score]
    top.sort(key=lambda c: (CATEGORY_PRECEDENCE.index(c)
                            if c in CATEGORY_PRECEDENCE
                            else len(CATEGORY_PRECEDENCE)))

    category = top[0]
    reason = _reason_for(description, category, matched[category])
    flag = "NEEDS_REVIEW" if len(top) > 1 else ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    One output row per source row. Rows that fail are recorded with
    category Other and flag NEEDS_REVIEW rather than crashing the batch.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        source_rows = list(reader)
        source_fields = reader.fieldnames or []

    results = []
    for row in source_rows:
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "category": "Other",
                "priority": "Standard",
                "reason": ("The row could not be processed; category "
                           "cannot be determined from the description."),
                "flag": "NEEDS_REVIEW",
            }
        output = dict(row)
        output.update({key: result[key] for key in
                       ("category", "priority", "reason", "flag")})
        results.append(output)

    fieldnames = list(source_fields) + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    count = batch_classify(args.input, args.output)
    print(f"Done. Classified {count} rows. Results written to {args.output}")