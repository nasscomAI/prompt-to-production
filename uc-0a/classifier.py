"""
UC-0A — Complaint Classifier
RICE → agents.md → skills.md → CRAFT implementation.
"""
import argparse
import csv
from typing import Dict

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
    description = row.get("description", "")
    flag = ""

    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = str(description).lower()

    # 1. Determine Priority based on severity keywords
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    is_urgent = len(matched_severity) > 0
    priority = "Urgent" if is_urgent else "Standard"

    # 2. Determine Category
    if "pothole" in desc_lower:
        category = "Pothole"
        cited_phrase = "pothole"
    elif any(k in desc_lower for k in ["heatwave", "44°c", "45°c", "52°c", "temperature", "full sun", "storing heat", "melting"]):
        category = "Heat Hazard"
        cited_phrase = "heat / temperature hazard"
    elif any(k in desc_lower for k in ["heritage", "historic", "ancient"]):
        category = "Heritage Damage"
        cited_phrase = "heritage asset"
    elif any(k in desc_lower for k in ["drain", "sewer", "gutter"]) and not ("underpass flooded" in desc_lower or "flooded after" in desc_lower or "floods in" in desc_lower):
        category = "Drain Blockage"
        cited_phrase = "drain blockage"
    elif any(k in desc_lower for k in ["flood", "flooded", "underpass", "rainwater", "waterlogging"]):
        category = "Flooding"
        cited_phrase = "flooding / water accumulation"
    elif any(k in desc_lower for k in ["streetlight", "light", "lights out", "darkness", "unlit", "dark at night"]):
        category = "Streetlight"
        cited_phrase = "lighting / streetlight issue"
    elif any(k in desc_lower for k in ["garbage", "waste", "dump", "bin", "trash", "dead animal"]):
        category = "Waste"
        cited_phrase = "waste overflow / garbage"
    elif any(k in desc_lower for k in ["noise", "music", "drilling", "sound", "amplifiers", "idling"]):
        category = "Noise"
        cited_phrase = "noise disturbance"
    elif any(k in desc_lower for k in ["road surface", "cracked", "sinking", "collapsed", "collapsing", "subsidence", "cobblestones", "footpath", "buckled", "tarmac", "paving", "manhole"]):
        category = "Road Damage"
        cited_phrase = "road surface / footpath damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cited_phrase = "unclassified issue"

    # Ensure category is strictly in ALLOWED_CATEGORIES
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Build concise single-sentence reason citing description words
    if matched_severity:
        reason = f"Classified as {category} ({priority}) citing words '{matched_severity[0]}' and '{cited_phrase}' in description."
    else:
        reason = f"Classified as {category} ({priority}) based on description detailing {cited_phrase}."

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
    Output headers: complaint_id, category, priority, reason, flag
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

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

