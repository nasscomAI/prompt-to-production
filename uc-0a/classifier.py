"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in agents.md and skills.md.
"""
import argparse
import csv
import re

# Enforcement: exact allowed category strings (agents.md)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Enforcement: keywords that must trigger Urgent priority (agents.md / README)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword map — ordered from most specific to least specific
CATEGORY_KEYWORDS = [
    ("Heritage Damage",  ["heritage", "monument", "historical", "historic"]),
    ("Heat Hazard",      ["heat", "temperature", "hot", "summer", "heatwave"]),
    ("Drain Blockage",   ["drain", "drainage", "sewer", "stormwater"]),
    ("Flooding",         ["flood", "flooded", "flooding", "waterlog", "submerged"]),
    ("Pothole",          ["pothole", "potholes"]),
    ("Road Damage",      ["road collapse", "road collapsed", "crater", "road damage", "road cracked"]),
    ("Streetlight",      ["streetlight", "street light", "lamp", "lighting", "light not working"]),
    ("Waste",            ["waste", "garbage", "trash", "rubbish", "litter", "dump", "debris"]),
    ("Noise",            ["noise", "drilling", "loud", "sound", "idling", "honking"]),
]


def _contains_keyword(text: str, keyword: str) -> bool:
    """Match keyword as a standalone token/phrase to reduce false positives."""
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text) is not None


def classify_complaint(row: dict) -> dict:
    """
    skill: classify_complaint
    Classifies a single complaint row into category, priority, reason, and flag.
    Input:  dict with at least a 'description' key.
    Output: dict with keys category, priority, reason, flag (plus original fields).
    """
    description = (row.get("description") or "").strip()

    # Error handling: missing or empty description
    if not description:
        return {
            **row,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Determine priority — Urgent if any severity keyword present
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if _contains_keyword(desc_lower, kw)]
    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Determine category — first matching keyword group wins
    category = None
    matched_keyword = None
    for cat, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if _contains_keyword(desc_lower, kw):
                category = cat
                matched_keyword = kw
                break
        if category:
            break

    # Ambiguity handling
    if category is None:
        cited_text = " ".join(description.split()[:8])
        return {
            **row,
            "category": "Other",
            "priority": priority,
            "reason": f"Category is ambiguous based on '{cited_text}' in description.",
            "flag": "NEEDS_REVIEW",
        }

    if category not in ALLOWED_CATEGORIES:
        return {
            **row,
            "category": "Other",
            "priority": priority,
            "reason": f"Mapped category '{category}' is invalid for allowed schema.",
            "flag": "NEEDS_REVIEW",
        }

    if priority not in ALLOWED_PRIORITIES:
        return {
            **row,
            "category": "Other",
            "priority": "Low",
            "reason": "Computed priority is invalid for allowed schema.",
            "flag": "NEEDS_REVIEW",
        }

    # Build reason citing specific words from description (enforcement rule)
    reason = (
        f"Classified as {category} based on '{matched_keyword}' in description"
        + (f"; priority set to Urgent due to '{matched_severity[0]}'" if matched_severity else "")
        + "."
    )

    return {
        **row,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    skill: batch_classify
    Reads input CSV, applies classify_complaint per row, writes results CSV.
    Does not crash on bad rows — records classification errors inline.
    """
    output_extra_fields = ["category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []
        fieldnames = list(dict.fromkeys(input_fields + output_extra_fields))
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:
            results.append({
                **row,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {exc}",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
