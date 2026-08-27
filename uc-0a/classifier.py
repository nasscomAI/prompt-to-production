"""
UC-0A — Complaint Classifier
Classifies citizen complaints into categories, priority, reason, and review flags.
"""
import argparse
import csv
import re
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = {
    "Pothole": ["pothole", "potholes", "road hole", "road cavity", "sinking road", "sinkhole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "water logging", "knee-deep", "submerged", "inundated"],
    "Streetlight": ["streetlight", "street light", "streetlights", "street lights", "lamp post", "light out", "lights out", "dark at night", "no lighting"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "overflowing bin", "dead animal", "rotting", "litter", "dumped"],
    "Noise": ["noise", "loud", "music", "blaring", "honking", "construction noise", "midnight", "loudspeaker"],
    "Road Damage": ["road cracked", "road surface", "road broken", "footpath", "pavement", "tiles broken", "cracked and sinking", "manhole cover missing"],
    "Heritage Damage": ["heritage", "monument", "historic", "ancient", "listed building", "conservation"],
    "Heat Hazard": ["heat", "heatwave", "scorching", "高温", "sunstroke", "dehydration", "extreme heat"],
    "Drain Blockage": ["drain blocked", "drainage blocked", "sewer blocked", "clogged drain", "blocked drain", "manhole overflow", "sewage"],
}


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row per agents.md enforcement rules."""
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description not provided.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Detect matching categories
    matched_categories = []
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                break

    # Determine category
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        # Ambiguous — pick first match, flag for review
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Determine priority based on severity keywords
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # Generate reason citing specific words from description
    reason = _generate_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _generate_reason(description: str, category: str) -> str:
    """Generate a one-sentence reason citing specific words from the description."""
    sentences = [s.strip() for s in description.split('.') if s.strip()]

    # Pick the most relevant sentence
    category_keywords = CATEGORY_RULES.get(category, [])
    best_sentence = sentences[0] if sentences else description

    for sentence in sentences:
        s_lower = sentence.lower()
        for kw in category_keywords:
            if kw in s_lower:
                best_sentence = sentence
                break

    # Truncate if too long
    if len(best_sentence) > 150:
        best_sentence = best_sentence[:147] + "..."

    return best_sentence + "."


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV per skills.md."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
