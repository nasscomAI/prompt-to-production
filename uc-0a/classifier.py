"""
UC-0A — Complaint Classifier
Reads test_[city].csv, classifies each complaint, writes results_[city].csv.
RICE enforcement: categories, priorities, reasons, flags enforced per rules.
"""
import csv
import sys
from typing import Dict, List, Tuple


ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "manhole"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "gutter", "clogged"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogging", "underpass flooded", "knee-deep", "standing in water", "rainwater", "draining"],
    "Streetlight": ["streetlight", "streetlights", "lights out", "flickering", "dark at night", "unlit", "darkness", "bulb", "lamp post"],
    "Waste": ["garbage", "waste", "trash", "bin", "bins", "dumped", "refuse", "dead animal"],
    "Noise": ["music", "loudspeaker", "noise", "decibel", "sound", "midnight", "drilling", "amplifiers", "audible"],
    "Heritage Damage": ["heritage", "monument", "historic", "statue", "defaced", "ancient"],
    "Heat Hazard": ["heatwave", "heat hazard", "sunstroke", "extreme heat", "44°c", "45°c", "52°c", "full sun", "melting"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "upturned", "pavement", "subsidence", "subsided", "cobblestones", "buckled"],
}

SEVERITY_KEYWORDS_URGENT = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Skill 1: classify_complaint
    Input: single complaint row dict
    Output: dict with keys complaint_id, category, priority, reason, flag
    """
    raw_desc = row.get("description", "")
    if not raw_desc or not raw_desc.strip():
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided in input row.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = raw_desc.lower()

    # Determine category matching
    matched_category = "Other"
    category_matched_words: List[str] = []

    for cat, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            matched_category = cat
            category_matched_words = matched
            break

    # Determine priority
    urgent_words = [kw for kw in SEVERITY_KEYWORDS_URGENT if kw in desc_lower]
    priority = "Urgent" if urgent_words else "Standard"

    # Build reason sentence
    reasons = []
    if category_matched_words:
        reasons.append(f"matched keywords '{', '.join(category_matched_words)}'")
    else:
        reasons.append("no standard category keywords found")

    if urgent_words:
        reasons.append(f"severity indicators '{', '.join(urgent_words)}'")

    reason = f"Classified based on {'; '.join(reasons)} in description."

    # Flag
    flag = "NEEDS_REVIEW" if matched_category == "Other" else ""

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Skill 2: batch_classify
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    rows = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    rows.append(result)
                except Exception as e:
                    # Skip malformed row safely
                    continue

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Classification complete. Output written to {args.output}")