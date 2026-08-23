"""
UC-0A — Complaint Classifier
Implementation of the RICE (Role, Intent, Context, Enforcement) agentic classification logic.
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
    "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row strictly following RICE enforcement rules.
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
            "reason": "Description field is empty.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Priority via Severity Keywords Rule
    priority = "Standard"
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) or kw in desc_lower:
            matched_severity.append(kw)
    
    if matched_severity:
        priority = "Urgent"

    # 2. Determine Category & Flag Rule
    category = "Other"
    flag = ""
    
    # Matching rules
    has_pothole = "pothole" in desc_lower
    has_flooding = any(w in desc_lower for w in ["flooded", "flooding", "waterlogging", "inaccessible", "floods"])
    has_drain = any(w in desc_lower for w in ["drain", "manhole", "sewer", "gutter", "drainage"])
    has_streetlight = any(w in desc_lower for w in ["streetlight", "streetlights", "lights out", "dark at night", "flickering"])
    has_waste = any(w in desc_lower for w in ["garbage", "waste", "trash", "bins", "dumped", "dead animal", "smell"])
    has_noise = any(w in desc_lower for w in ["music", "noise", "loudspeaker", "sound", "midnight"])
    has_road = any(w in desc_lower for w in ["road surface", "cracked", "footpath", "tiles", "sinking", "asphalt"])
    has_heritage = "heritage" in desc_lower
    has_heat = any(w in desc_lower for w in ["heatwave", "heat hazard", "extreme heat"])

    categories_matched = []
    if has_pothole:
        categories_matched.append("Pothole")
    if has_flooding:
        categories_matched.append("Flooding")
    if has_drain:
        categories_matched.append("Drain Blockage")
    if has_streetlight:
        categories_matched.append("Streetlight")
    if has_waste:
        categories_matched.append("Waste")
    if has_noise:
        categories_matched.append("Noise")
    if has_road:
        categories_matched.append("Road Damage")
    if has_heritage:
        categories_matched.append("Heritage Damage")
    if has_heat:
        categories_matched.append("Heat Hazard")

    if len(categories_matched) == 1:
        category = categories_matched[0]
    elif len(categories_matched) > 1:
        # Ambiguous case or dominant primary category
        if "Pothole" in categories_matched:
            category = "Pothole"
        elif "Drain Blockage" in categories_matched and "Flooding" in categories_matched:
            category = "Drain Blockage"
        elif "Heritage Damage" in categories_matched and "Streetlight" in categories_matched:
            category = "Streetlight"
            flag = "NEEDS_REVIEW"
        else:
            category = categories_matched[0]
            flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Enforce allowed values check
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Formulate Reason (One sentence citing specific words)
    if matched_severity:
        reason = f"Cites '{matched_severity[0]}' in complaint description indicating critical public safety risk."
    else:
        # Quote key phrase
        reason = f"Cites '{description[:45]}...' from citizen complaint description."

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
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except PermissionError:
        print(f"Error: Permission denied writing to '{output_path}'.")
        print("Please close the CSV file if it is currently open in Excel or another application, then run the command again.")
        return

    print(f"Batch classification complete. Processed {len(results)} rows -> Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
