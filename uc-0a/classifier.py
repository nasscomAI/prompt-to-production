"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category and priority with severity detection.
Built using RICE + agents.md + skills.md workflow.
"""
import argparse
import csv
import re
from pathlib import Path

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "road hole", "road damaged"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "water logging", "rainwater"],
    "Streetlight": ["streetlight", "street light", "lamp post", "light not working", "no light", "dark"],
    "Waste": ["garbage", "waste", "rubbish", "trash", "litter", "overflow", "not cleared", "uncollected"],
    "Noise": ["noise", "drilling", "loud", "idling", "honking", "construction noise"],
    "Road Damage": ["road collapsed", "road damage", "crater", "road surface", "asphalt"],
    "Heritage Damage": ["heritage", "heritage zone", "monument", "protected structure"],
    "Heat Hazard": ["heat", "heatwave", "scorching", "sunstroke", "dehydration"],
    "Drain Blockage": ["drain blocked", "drainage blocked", "blocked drain", "drainage", "sewer", "mosquito breeding"],
}

AMBIGUOUS_DESCRIPTIONS = [
    "multiple issues",
    "several problems",
    "unclear",
]


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row into category, priority, reason, flag."""
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category = _detect_category(desc_lower)
    priority = _detect_priority(desc_lower)
    flag = _detect_ambiguity(desc_lower, category)
    reason = _generate_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _detect_category(desc_lower: str) -> str:
    """Detect category from description using keyword matching."""
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            scores[cat] = score

    if not scores:
        return "Other"

    max_score = max(scores.values())
    top_cats = [cat for cat, s in scores.items() if s == max_score]

    if len(top_cats) > 1:
        return "Other"

    return top_cats[0]


def _detect_priority(desc_lower: str) -> str:
    """Detect priority based on severity keywords."""
    for keyword in SEVERITY_KEYWORDS:
        if keyword in desc_lower:
            return "Urgent"
    return "Standard"


def _detect_ambiguity(desc_lower: str, category: str) -> str:
    """Flag ambiguous complaints for review."""
    if category == "Other":
        return "NEEDS_REVIEW"

    for phrase in AMBIGUOUS_DESCRIPTIONS:
        if phrase in desc_lower:
            return "NEEDS_REVIEW"

    return ""


def _generate_reason(description: str, category: str) -> str:
    """Generate a reason citing specific words from the description."""
    words = description.split()
    cited_words = []

    category_triggers = {
        "Pothole": ["pothole", "potholes", "crater"],
        "Flooding": ["flood", "flooded", "flooding", "waterlogged", "rainwater"],
        "Streetlight": ["streetlight", "street light", "lamp", "light"],
        "Waste": ["garbage", "waste", "rubbish", "trash", "overflow", "cleared"],
        "Noise": ["drilling", "loud", "idling", "noise", "honking"],
        "Road Damage": ["collapsed", "crater", "road", "damage"],
        "Heritage Damage": ["heritage", "monument", "protected"],
        "Heat Hazard": ["heat", "heatwave", "sunstroke"],
        "Drain Blockage": ["drain", "blocked", "drainage", "mosquito", "sewer"],
        "Other": [],
    }

    triggers = category_triggers.get(category, [])
    for word in words:
        word_lower = word.lower().strip(".,;:!?")
        if any(t in word_lower for t in triggers):
            cited_words.append(word)

    if cited_words:
        return f"Classified as {category} based on: {', '.join(cited_words[:5])}."
    return f"Classified as {category} based on complaint description."


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    filepath = Path(input_path)
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
                rows.append(result)
            except Exception as e:
                rows.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Classified {len(rows)} complaints.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
