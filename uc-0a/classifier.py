"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "injuries", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "hazards", "fell", "collapse",
    "collapsed", "collapsing",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "potholes"]),
    ("Flooding", ["flood", "floods", "flooding", "flooded", "waterlog", "waterlogged"]),
    ("Streetlight", ["unlit", "streetlight", "streetlights", "streetlighting", "illumination", "wiring theft", "lights"]),
    ("Waste", ["waste", "garbage", "trash", "bin overflow", "bins overflowing"]),
    ("Noise", ["noise", "noisy", "loud", "music", "audible"]),
    ("Heritage Damage", ["heritage", "historic", "ancient", "historical", "step well"]),
    ("Road Damage", ["road surface", "road collapsed", "road subsidence", "road bubbling", "upturned paving", "bubbling", "subsidence", "subsided", "footpath", "sinking"]),
    ("Heat Hazard", ["temperatures", "heat", "burning", "sun", "hot", "melting", "\u00b0c"]),
    ("Drain Blockage", ["drain", "drainage block", "drains"]),
]


def normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9\s\u00b0]', '', text.lower())


def _has_word(text: str, word: str) -> bool:
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text))


def get_category(description: str) -> str:
    desc = normalize(description)
    if not desc.strip():
        return "Other"
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if " " in kw:
                if kw.lower() in desc:
                    return cat
            else:
                if _has_word(desc, kw.lower()):
                    return cat
    return "Other"


def get_priority(description: str) -> str:
    desc = normalize(description)
    for kw in SEVERITY_KEYWORDS:
        if _has_word(desc, kw):
            return "Urgent"
    return "Standard"


def get_reason(description: str, category: str) -> str:
    if not description or not description.strip():
        return "No description provided."
    first_sentence = description.split('.')[0].strip()
    if not first_sentence:
        first_sentence = description.strip()[:80]
    return f"Complaint about {category.lower()}: \"{first_sentence}\""


def get_flag(description: str) -> str:
    if not description or not description.strip():
        return "NEEDS_REVIEW"
    desc = normalize(description)
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if " " in kw:
                if kw.lower() in desc:
                    return ""
            else:
                if _has_word(desc, kw.lower()):
                    return ""
    return "NEEDS_REVIEW"


def classify_complaint(row: dict) -> dict:
    desc = (row.get("description") or "").strip()
    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }
    category = get_category(desc)
    priority = get_priority(desc)
    reason = get_reason(desc, category)
    flag = get_flag(desc)
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
                rows.append(result)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', '?')}: {e}")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Done. {len(rows)} rows written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
