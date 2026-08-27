"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

CATEGORY_RULES = [
    ("Pothole",       ["pothole"]),
    ("Streetlight",   ["streetlight", "street light", "lights out", "flicker", "sparking", "dark at night"]),
    ("Flooding",      ["flood", "submerged", "knee-deep", "standing in water"]),
    ("Drain Blockage",["drain", "blocked drain", "manhole", "sewer"]),
    ("Waste",         ["garbage", "waste", "overflowing bin", "dead animal", "dumping", "rubbish", "trash"]),
    ("Noise",         ["music", "noise", "amplif", "loud", "wedding band", "wedding venue"]),
    ("Road Damage",   ["road surface", "cracked", "sinking", "subsided", "buckled", "collapsed", "collapsing", "footpath", "paving", "broken"]),
    ("Heritage Damage",["heritage"]),
    ("Heat Hazard",   ["heat", "heatwave", "temperature"]),
]

DEFAULT_CATEGORY = "Other"


def _contains_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    for kw in keywords:
        if " " in kw:
            if kw in lower:
                return True
        elif len(kw) <= 4:
            if re.search(rf"\b{re.escape(kw)}\b", lower):
                return True
        else:
            if kw in lower:
                return True
    return False


def _check_priority(description: str) -> str:
    if not description:
        return "Standard"
    lower = description.lower()
    if any(kw in lower for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _determine_category(description: str, location: str) -> str:
    if not description:
        return DEFAULT_CATEGORY

    combined = f"{description} {location}"
    matched = [name for name, keywords in CATEGORY_RULES if _contains_any(combined, keywords)]

    if len(matched) == 1:
        return matched[0]
    if len(matched) > 1:
        return "Other"
    return DEFAULT_CATEGORY


def _generate_reason(description: str, category: str) -> str:
    if not description:
        return "No description provided"
    words = description.split()
    cited = [w.strip(".,;:!?\"'") for w in words if len(w.strip(".,;:!?\"'")) > 3][:8]
    if cited:
        return f"The complaint describes {', '.join(cited[:4])} which indicates {category.lower().replace('_', ' ')}."
    return f"The complaint relates to {category.lower().replace('_', ' ')}."


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").strip()
    location = (row.get("location") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    category = _determine_category(description, location)
    priority = _check_priority(description)
    reason = _generate_reason(description, category)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Error processing row",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
