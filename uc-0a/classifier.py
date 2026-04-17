"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Enforcement: exact allowed category strings (agents.md)
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Enforcement: whole-word urgency keywords that force Urgent priority (agents.md)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword map — ordered, one match per category per description
# First keyword hit for each category wins; multiple category matches → NEEDS_REVIEW
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Pothole":         ["pothole"],
    "Flooding":        ["flooded", "flooding", "flood", "waterlogged", "submerged", "inundated"],
    "Streetlight":     ["streetlight", "street light", "street lamp", "lamp post", "light out", "lights out"],
    "Waste":           ["garbage", "rubbish", "litter", "trash", "overflowing bin", "garbage bin", "waste"],
    "Noise":           ["music", "noise", "loud", "blaring"],
    "Road Damage":     ["road surface", "cracked road", "road crack", "road damage", "sinking road", "road sinking", "cracked and sinking"],
    "Heritage Damage": ["heritage", "monument", "historical building", "ancient structure"],
    "Heat Hazard":     ["heatwave", "heat wave", "extreme heat", "heat hazard", "heatstroke"],
    "Drain Blockage":  ["drain blocked", "blocked drain", "drain choked", "drainage blocked", "clogged drain"],
}


def _whole_word_match(keyword: str, text: str) -> bool:
    """Return True if keyword appears as a whole word in text (case-insensitive)."""
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    # Enforcement: null/empty description → Other, Low, NEEDS_REVIEW (agents.md + skills.md)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description was provided; unable to classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Detect category — collect all matching categories
    category_matches: list[tuple[str, str]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in desc_lower:
                category_matches.append((category, kw))
                break  # one match per category is sufficient

    flag = ""
    if len(category_matches) == 0:
        category, cat_kw = "Other", ""
        flag = "NEEDS_REVIEW"
    elif len(category_matches) == 1:
        category, cat_kw = category_matches[0]
    else:
        # Multiple matches — best guess is first; flag for human review (agents.md enforcement)
        category, cat_kw = category_matches[0]
        flag = "NEEDS_REVIEW"

    # Enforcement: whole-word urgency keyword check forces Urgent (agents.md)
    matched_urgent = [kw for kw in URGENT_KEYWORDS if _whole_word_match(kw, description)]
    if matched_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Build reason: one sentence citing specific words from the description (agents.md)
    if matched_urgent and cat_kw:
        reason = (
            f"Description mentions '{cat_kw}' indicating {category}, "
            f"and contains urgency keyword '{matched_urgent[0]}'."
        )
    elif matched_urgent:
        reason = (
            f"Description contains urgency keyword '{matched_urgent[0]}'; "
            f"classified as {category} based on overall context."
        )
    elif cat_kw:
        reason = f"Description mentions '{cat_kw}', indicating category {category}."
    else:
        reason = "Description did not match any known category keywords; classified as Other."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Wraps each row in try/except — never crashes the full batch on a single bad row.
    """
    output_rows: list[dict] = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            output_rows.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
