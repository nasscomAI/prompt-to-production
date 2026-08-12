"""
UC-0A — Complaint Classifier
RICE → agents.md → skills.md → CRAFT implementation.
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
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to RICE rules:
    - Allowed categories exact match
    - Severity keyword check for Urgent priority
    - Single-sentence justification citing specific words
    - Flag as NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    
    # 1. Determine priority based on severity keywords
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"
    
    # 2. Category matching logic
    cat = "Other"
    flag = ""
    reasons = []

    # Checks
    is_pothole = "pothole" in desc_lower
    is_flooding = "flood" in desc_lower or "water" in desc_lower
    is_streetlight = "light" in desc_lower or "dark" in desc_lower or "sparking" in desc_lower
    is_waste = "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower or "dumped" in desc_lower or "dead animal" in desc_lower
    is_noise = "music" in desc_lower or "noise" in desc_lower or "loud" in desc_lower or "drilling" in desc_lower or "idling" in desc_lower
    is_road_damage = "cracked" in desc_lower or "sinking" in desc_lower or "footpath" in desc_lower or "tiles broken" in desc_lower or "road surface" in desc_lower or "collapsed" in desc_lower or "crater" in desc_lower
    is_heritage = "heritage" in desc_lower
    is_heat = "heat" in desc_lower
    is_drain = "drain" in desc_lower or "manhole" in desc_lower
    
    matched_categories = []
    if is_pothole: matched_categories.append("Pothole")
    if is_flooding: matched_categories.append("Flooding")
    if is_streetlight: matched_categories.append("Streetlight")
    if is_waste: matched_categories.append("Waste")
    if is_noise: matched_categories.append("Noise")
    if is_road_damage and not is_pothole: matched_categories.append("Road Damage")
    if is_heritage: matched_categories.append("Heritage Damage")
    if is_heat: matched_categories.append("Heat Hazard")
    if is_drain and not is_flooding: matched_categories.append("Drain Blockage")

    if len(matched_categories) == 1:
        cat = matched_categories[0]
    elif len(matched_categories) > 1:
        # Heritage overrides or lights out on heritage street
        if "Heritage Damage" in matched_categories:
            cat = "Heritage Damage"
            flag = "NEEDS_REVIEW"
        elif "Pothole" in matched_categories:
            cat = "Pothole"
        elif "Flooding" in matched_categories:
            cat = "Flooding"
        else:
            cat = matched_categories[0]
            flag = "NEEDS_REVIEW"
    else:
        # Fallback keyword checks
        if "manhole" in desc_lower or "drain" in desc_lower:
            cat = "Drain Blockage"
        elif "animal" in desc_lower or "garbage" in desc_lower:
            cat = "Waste"
        else:
            cat = "Other"
            flag = "NEEDS_REVIEW"

    # Citation sentence
    quoted_words = []
    for word in re.findall(r'\b\w+\b', description):
        if word.lower() in desc_lower and word.lower() in [
            "pothole", "flooded", "flooding", "water", "streetlights", "lights", "garbage",
            "waste", "music", "cracked", "sinking", "manhole", "drain", "heritage", "child",
            "children", "school", "fell", "injury", "hazard", "dark", "bus", "underpass"
        ]:
            if word not in quoted_words:
                quoted_words.append(word)

    if quoted_words:
        cited_str = ", ".join([f"'{w}'" for w in quoted_words[:3]])
        reason = f"Classified as {cat} with {priority} priority due to key terms {cited_str} in description."
    else:
        reason = f"Classified as {cat} with {priority} priority based on issue description."

    return {
        "complaint_id": complaint_id,
        "category": cat,
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
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    # Ensure directory exists for output
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Batch classification complete. {len(results)} rows processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
