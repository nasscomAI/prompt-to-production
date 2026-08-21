"""
UC-0A — Complaint Classifier
Rule-based enforcement adhering to RICE specifications.
"""
import argparse
import csv
import re
import os

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

URGENT_KEYWORDS = [
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
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description in input row.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # 1. Determine Priority
    urgent_matches = [kw for kw in URGENT_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)]
    if urgent_matches:
        priority = "Urgent"
    else:
        # Default standard unless low urgency indicator
        if any(w in desc_lower for w in ["music", "minor", "inconvenience"]):
            priority = "Low"
        else:
            priority = "Standard"

    # 2. Determine Category & Citations
    category = "Other"
    reason = ""
    flag = ""

    # Category matching rules
    if "pothole" in desc_lower or "pot hole" in desc_lower:
        category = "Pothole"
        reason = f"Pothole issue identified: '{description}'"
    elif "drain blocked" in desc_lower or "drain blockage" in desc_lower or "drainage" in desc_lower:
        category = "Drain Blockage"
        reason = f"Drain blockage reported: '{description}'"
    elif any(w in desc_lower for w in ["flooded", "flooding", "flood", "waterlogging", "standing in water"]):
        category = "Flooding"
        reason = f"Flooding condition reported: '{description}'"
    elif any(w in desc_lower for w in ["streetlight", "street light", "lights out", "flickering", "sparking"]):
        category = "Streetlight"
        reason = f"Streetlight lighting issue reported: '{description}'"
    elif any(w in desc_lower for w in ["garbage", "waste", "dumped", "dead animal", "trash", "litter"]):
        category = "Waste"
        reason = f"Waste management issue reported: '{description}'"
    elif any(w in desc_lower for w in ["music", "noise", "loudspeaker", "sound"]):
        category = "Noise"
        reason = f"Noise complaint reported: '{description}'"
    elif any(w in desc_lower for w in ["heritage", "monument", "historic"]):
        category = "Heritage Damage"
        reason = f"Heritage structure concern: '{description}'"
    elif any(w in desc_lower for w in ["heatwave", "extreme heat", "sunstroke"]):
        category = "Heat Hazard"
        reason = f"Heat hazard reported: '{description}'"
    elif any(w in desc_lower for w in ["road surface", "cracked", "sinking", "manhole", "footpath", "pavement", "broken tiles", "tiles broken"]):
        category = "Road Damage"
        reason = f"Road or footpath damage reported: '{description}'"
    else:
        category = "Other"
        reason = f"Could not unambiguously determine category from: '{description}'"
        flag = "NEEDS_REVIEW"

    # Ambiguity check (e.g. mentions multiple domain categories like heritage street + lights out)
    if "heritage street" in desc_lower and "lights out" in desc_lower:
        category = "Streetlight"
        flag = "NEEDS_REVIEW"
        reason = f"Streetlight issue on heritage street ('{description}')"

    # Ensure category is strictly in allowed categories
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
                # Never crash on bad rows
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error parsing row: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

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
