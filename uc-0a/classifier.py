"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "hole in road", "road hole", "deep hole"],
    "Flooding": ["flood", "flooding", "flooded", "waterlogged", "water logging", "standing water", "inundated", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "street lamp", "lamp post", "light not working", "light pole", "lights out", "flickering", "darkness", "substation tripped", "power outage", "unlit"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumping", "refuse", "rubbish", "debris", "dead animal", "overflowing"],
    "Noise": ["noise", "loud", "sound", "disturbance", "honking", "loudspeaker", "music", "construction noise", "past midnight", "amplifier", "band playing", "11pm", "10pm"],
    "Road Damage": ["crack", "cracked", "road damage", "surface damage", "broken road", "road broken", "pavement damage", "footpath", "pavement", "tiles broken", "upturned", "sinking", "buckled", "subsided", "cobblestone"],
    "Heritage Damage": ["heritage", "monument", "historical", "heritage site", "monument damage", "old city", "historic", "heritage zone", "heritage stone", "defaced"],
    "Heat Hazard": ["heat", "hot surface", "heat hazard", "burning", "overheat", "scorching", "melting", "temperature", "bubbling", "44", "45", "46", "47", "48", "49", "50"],
    "Drain Blockage": ["drain", "blocked drain", "drainage", "sewage", "clogged drain", "manhole", "drain block", "manhole cover"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "") or ""
    description_lower = description.lower().strip()

    if not description_lower:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    category, is_tied = _determine_category(description_lower)
    priority = _determine_priority(description_lower, category)
    reason = _generate_reason(description, category)
    is_vague = not _is_unambiguous(description_lower)
    flag = "NEEDS_REVIEW" if (is_tied or is_vague) else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _determine_category(description_lower: str) -> tuple:
    """Returns (category, is_ambiguous) where is_ambiguous indicates a tie."""
    best_category = "Other"
    best_score = 0
    ties = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in description_lower)
        if score > best_score:
            best_score = score
            best_category = category
            ties = [category]
        elif score == best_score and score > 0:
            ties.append(category)

    if best_score == 0:
        return "Other", True  # no category matched

    return best_category, len(ties) > 1


def _determine_priority(description_lower: str, category: str) -> str:
    for kw in URGENT_KEYWORDS:
        if kw in description_lower:
            return "Urgent"

    if category in ("Other",):
        return "Low"

    traffic_safety_categories = {"Pothole", "Flooding", "Road Damage", "Heat Hazard", "Drain Blockage", "Streetlight"}
    if category in traffic_safety_categories:
        return "Standard"

    minor_categories = {"Noise", "Waste", "Heritage Damage"}
    if category in minor_categories:
        return "Low"

    return "Standard"


def _generate_reason(description: str, category: str) -> str:
    words = description.split()
    snippet = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
    return f"Classified as {category} based on description: '{snippet}'"


def _is_unambiguous(description_lower: str) -> bool:
    vague_phrases = ["problem", "issue", "something wrong", "not good", "bad condition"]
    match_count = sum(1 for phrase in vague_phrases if phrase in description_lower)
    keyword_matches = sum(1 for kws in CATEGORY_KEYWORDS.values() for kw in kws if kw in description_lower)
    return keyword_matches >= 1 and match_count <= 0


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles nulls, bad rows, and produces output even if some rows fail.
    """
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", f"UNKNOWN_ROW_{row_num}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
