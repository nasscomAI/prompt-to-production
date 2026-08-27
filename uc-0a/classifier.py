"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import sys
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "hole in road", "road hole", "tyre damage", "wheel damage"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "water logging", "knee-deep", "submerged", "inundated"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "flickering", "lamp", "no lighting", "dark at night"],
    "Waste": ["garbage", "waste", "overflowing", "bins", "trash", "rubbish", "dead animal", "rotting", "smell", "dumped"],
    "Noise": ["noise", "loud", "music", "dj", "firecracker", "midnight", "barking", "honking", "construction noise"],
    "Road Damage": ["road cracked", "cracked road", "sinking", "road surface", "asphalt", "road broken", "footpath", "tiles broken", "road collapse"],
    "Heritage Damage": ["heritage", "historic", "monument", "old structure", "heritage street", "heritage building"],
    "Heat Hazard": ["heat", "heatwave", "scorching", "sunstroke", "dehydration", "extreme heat"],
    "Drain Blockage": ["drain blocked", "blocked drain", "sewer", "manhole", "drainage", "clogged drain", "overflowing drain"],
}

CATEGORY_AMBIGUITY = {
    ("Pothole", "Road Damage"): ["pothole", "road", "crack", "sinking"],
    ("Flooding", "Drain Blockage"): ["flood", "drain", "water", "blocked"],
    ("Streetlight", "Heritage Damage"): ["lights", "heritage", "old", "street"],
    ("Waste", "Drain Blockage"): ["garbage", "drain", "overflow", "blocked"],
}


def _find_keywords(text: str, keywords: list) -> list:
    """Return list of keywords found in text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def _extract_citations(text: str, count: int = 2) -> str:
    """Extract specific phrases from description for the reason field."""
    sentences = re.split(r'[.!]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

    if not sentences:
        return text.strip()[:100] if text.strip() else "No description provided"

    if len(sentences) >= count:
        return ". ".join(sentences[:count]) + "."
    return sentences[0] + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    matched_categories = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                break

    if not matched_categories:
        matched_categories.append("Other")

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"

    severity_found = _find_keywords(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity_found else "Standard"

    reason = _extract_citations(description)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Row {i} failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
