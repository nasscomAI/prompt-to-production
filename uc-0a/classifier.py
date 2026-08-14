"""
UC-0A — Complaint Classifier
Implementation based on RICE prompt (agents.md) and skill specifications (skills.md).
"""
import argparse
import csv
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

SEVERITY_KEYWORDS = [
    "injury",
    "injured",
    "child",
    "children",
    "school",
    "hospital",
    "hospitalised",
    "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    desc_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty description in input record.",
            "flag": "NEEDS_REVIEW",
        }

    # 1. Category Classification based on taxonomy rules
    category = "Other"
    if any(k in desc_lower for k in ["heritage", "historic", "ancient", "museum"]):
        category = "Heritage Damage"
    elif any(k in desc_lower for k in ["heat", "44°c", "45°c", "52°c", "temperature", "heatwave", "sun"]):
        category = "Heat Hazard"
    elif "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
    elif "drain" in desc_lower and ("block" in desc_lower or "clog" in desc_lower):
        category = "Drain Blockage"
    elif any(k in desc_lower for k in ["flood", "flooded", "flooding", "waterlog", "waterlogged"]):
        category = "Flooding"
    elif any(k in desc_lower for k in ["streetlight", "streetlights", "lamp post", "unlit", "darkness", "lights out"]):
        category = "Streetlight"
    elif any(k in desc_lower for k in ["garbage", "waste", "bin", "bins", "dumped", "dead animal"]):
        category = "Waste"
    elif any(k in desc_lower for k in ["music", "drilling", "amplifier", "sound", "noise"]):
        category = "Noise"
    elif any(k in desc_lower for k in ["crack", "sinking", "manhole", "footpath", "tile", "tarmac", "paving", "subsided", "subsidence", "buckled", "road"]):
        category = "Road Damage"

    # 2. Priority Classification based on severity trigger keywords
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_severity:
        priority = "Urgent"
        reason = f"Classified as '{category}' with Urgent priority due to severity keyword '{matched_severity[0]}' in description."
    else:
        priority = "Standard"
        reason = f"Classified as '{category}' with Standard priority based on description text."

    # 3. Refusal & Review Flagging
    flag = "NEEDS_REVIEW" if category == "Other" else ""

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
    Includes fallback error handling to avoid batch failure on corrupt rows.
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
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error encountered: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

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

