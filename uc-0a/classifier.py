"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
from typing import Dict, Optional

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

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "flooded", "flooding", "waterlogging", "waterlogged", "inundat"]),
    ("Streetlight", ["streetlight", "street light", "streetlights", "lights out", "light out", "lamp", "flickering", "sparking"]),
    ("Waste", ["garbage", "waste", "bins", "dumped", "dumping", "trash", "rubbish"]),
    ("Noise", ["noise", "music", "loud", "sound"]),
    ("Road Damage", ["road", "crack", "cracked", "surface", "sinking", "sink", "tiles", "footpath", "upturned", "broken"]),
    ("Heritage Damage", ["heritage", "historic", "monument"]),
    ("Heat Hazard", ["heat", "hot", "sun", "temperature"]),
    ("Drain Blockage", ["drain", "blocked", "blockage", "manhole", "sewer", "clog", "clogged"]),
]


def classify_complaint(row: Optional[dict]) -> dict:
    """Classify a single complaint row into the required schema."""
    if not row:
        row = {}

    description = str(row.get("description", "") or "")
    complaint_id = str(row.get("complaint_id", "") or "")

    normalized = description.lower()
    matched_categories = []

    for category, keywords in CATEGORY_RULES:
        if any(keyword in normalized for keyword in keywords):
            matched_categories.append(category)

    category = "Other"
    flag = ""

    if matched_categories:
        if len(matched_categories) == 1:
            category = matched_categories[0]
        else:
            # Prefer the more specific category when multiple signals appear.
            if "Flooding" in matched_categories and "Drain Blockage" in matched_categories:
                category = "Flooding"
            elif "Streetlight" in matched_categories and "Heritage Damage" in matched_categories:
                category = "Streetlight"
            else:
                category = matched_categories[0]
                flag = "NEEDS_REVIEW"
    else:
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if any(keyword in normalized for keyword in URGENT_KEYWORDS) else "Standard"

    if category == "Other" and not matched_categories:
        reason = "The description does not contain enough clear category keywords to assign a specific category."
    elif category == "Road Damage" and "cracked" in normalized:
        reason = "The description mentions 'cracked' road surface, which fits Road Damage."
    elif category == "Streetlight" and "flickering" in normalized:
        reason = "The description mentions 'flickering' and 'sparking', which point to Streetlight."
    elif category == "Flooding" and "flooded" in normalized:
        reason = "The description mentions 'flooded', which clearly indicates Flooding."
    elif category == "Pothole" and "pothole" in normalized:
        reason = "The description mentions 'pothole', which matches Pothole."
    elif category == "Waste" and any(word in normalized for word in ["garbage", "bins", "waste"]):
        reason = "The description mentions 'garbage' or 'bins', which fits Waste."
    elif category == "Noise" and any(word in normalized for word in ["music", "noise"]):
        reason = "The description mentions 'music' or 'noise', which fits Noise."
    elif category == "Drain Blockage" and any(word in normalized for word in ["drain", "blocked", "manhole"]):
        reason = "The description mentions 'drain' or 'blocked', which fits Drain Blockage."
    elif category == "Heritage Damage" and any(word in normalized for word in ["heritage", "historic"]):
        reason = "The description mentions 'heritage', which fits Heritage Damage."
    elif category == "Heat Hazard" and any(word in normalized for word in ["heat", "hot"]):
        reason = "The description mentions 'heat' or 'hot', which fits Heat Hazard."
    else:
        evidence = next((keyword for keyword in ["pothole", "flooded", "streetlight", "garbage", "noise", "cracked", "heritage", "heat", "drain", "blocked", "lights", "music"] if keyword in normalized), "issue")
        reason = f"The description mentions '{evidence}', which supports {category}."

    if priority == "Urgent":
        matched_keywords = [kw for kw in URGENT_KEYWORDS if kw in normalized]
        if matched_keywords:
            severity_words = ", ".join(matched_keywords[:3])
            reason = f"{reason} The description also includes severity cues such as '{severity_words}'."
        else:
            reason = f"{reason} The description also includes a severity cue."

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read the input CSV, classify each row, and write results CSV."""
    try:
        with open(input_path, "r", encoding="utf-8", newline="") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = output_path.rsplit("/", 1)[0] if "/" in output_path else "."
    if output_dir and output_dir != ".":
        import os
        os.makedirs(output_dir, exist_ok=True)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            results.append({
                "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                "category": "Other",
                "priority": "Standard",
                "reason": "The row could not be classified reliably.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
