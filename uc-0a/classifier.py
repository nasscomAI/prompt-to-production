"""
UC-0A — Complaint Classifier
Implementation based on agents.md (RICE framework) and skills.md.
"""
import argparse
import csv
import os
import re

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or empty complaint description text.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # 1. Priority Enforcement: Urgent if severity keywords are present
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    # 2. Category Matching Rules
    category_scores = {}

    def score_category(cat: str, points: int):
        category_scores[cat] = category_scores.get(cat, 0) + points

    # Heat Hazard
    if any(k in desc_lower for k in ["heat", "temperature", "44°c", "45°c", "52°c", "melting", "heatwave", "burns", "full sun"]):
        score_category("Heat Hazard", 3)

    # Heritage Damage
    if any(k in desc_lower for k in ["heritage", "historic", "cobblestones", "ancient", "museum", "precinct", "deface"]):
        score_category("Heritage Damage", 3)

    # Pothole
    if any(k in desc_lower for k in ["pothole", "potholes", "crater"]):
        score_category("Pothole", 3)

    # Flooding
    if any(k in desc_lower for k in ["flood", "flooded", "flooding", "waterlogging", "underpass flooded"]):
        score_category("Flooding", 3)

    # Drain Blockage
    if any(k in desc_lower for k in ["drain", "drainage", "stormwater drain", "manhole", "sewer"]):
        score_category("Drain Blockage", 3)

    # Streetlight
    if any(k in desc_lower for k in ["streetlight", "streetlights", "lamp post", "unlit", "substation tripped", "darkness", "lights out", "wiring theft"]):
        score_category("Streetlight", 3)

    # Waste
    if any(k in desc_lower for k in ["garbage", "waste", "bins", "dumped", "dead animal", "smell", "piles of waste"]):
        score_category("Waste", 3)

    # Noise
    if any(k in desc_lower for k in ["music", "noise", "drilling", "sound", "amplifiers", "idling", "loud"]):
        score_category("Noise", 3)

    # Road Damage
    if any(k in desc_lower for k in ["road surface", "cracked", "sinking", "subsidence", "subsided", "footpath", "buckled", "road collapsed", "tarmac"]):
        score_category("Road Damage", 3)

    # Selection & Ambiguity Flagging
    flag = ""
    if not category_scores:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # Sort categories by score
        sorted_cats = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
        top_category, top_score = sorted_cats[0]
        category = top_category

        # Flag as NEEDS_REVIEW if top 2 categories have equal top score
        if len(sorted_cats) > 1 and sorted_cats[1][1] == top_score:
            flag = "NEEDS_REVIEW"

    # Schema Validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Single-sentence reason citing exact words from description
    snippet = description if len(description) <= 80 else description[:77] + "..."
    reason = f'Classified based on complaint description: "{snippet}".'

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Fallback for corrupt rows without crashing
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing failed due to error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

    # Create directory if needed
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
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
