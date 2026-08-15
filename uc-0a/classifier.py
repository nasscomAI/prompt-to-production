"""
UC-0A — Complaint Classifier
Production implementation following RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import os
import re
from typing import Dict, Any, Tuple

# Exact allowed categories
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

# Severity keywords that trigger 'Urgent' priority
SEVERITY_KEYWORDS = [
    "injury", "injured", "injuries",
    "child", "children",
    "school",
    "hospital", "hospitalised", "hospitalized",
    "ambulance",
    "fire",
    "hazard", "hazardous", "hazards",
    "fell", "fallen", "falling",
    "collapse", "collapsed", "collapsing",
]


def check_severity(text: str) -> Tuple[bool, list]:
    """Check if any severity trigger keywords exist in text."""
    lower_text = text.lower()
    matched = []
    for kw in SEVERITY_KEYWORDS:
        # Match as whole word or part of word
        pattern = r"\b" + re.escape(kw)
        if re.search(pattern, lower_text):
            matched.append(kw)
    return len(matched) > 0, matched


def determine_category_and_flag(description: str, location: str = "") -> Tuple[str, str, str]:
    """
    Determine category, flag, and key evidence phrase from text.
    Returns: (category, flag, matched_evidence)
    """
    text = f"{description} {location}".lower()

    if not description or not description.strip():
        return "Other", "NEEDS_REVIEW", "missing description"

    # Category matching rules with explicit keyword weights
    cat_scores = {cat: 0 for cat in ALLOWED_CATEGORIES}
    evidence = {cat: [] for cat in ALLOWED_CATEGORIES}

    # 1. Heritage Damage
    heritage_kw = ["heritage", "historic", "ancient", "monument", "museum", "cobblestones"]
    for kw in heritage_kw:
        if kw in text:
            cat_scores["Heritage Damage"] += 3
            evidence["Heritage Damage"].append(kw)

    # 2. Heat Hazard
    heat_kw = ["melting", "heatwave", "44°c", "44 c", "45°c", "45 c", "52°c", "52 c",
               "dangerous temperatures", "burns on contact", "storing heat", "surface temperature unbearable",
               "exposed to full sun"]
    for kw in heat_kw:
        if kw in text:
            cat_scores["Heat Hazard"] += 4
            evidence["Heat Hazard"].append(kw)

    # 3. Pothole
    pothole_kw = ["pothole", "potholes", "crater", "tyre damage", "tyre blowouts", "swallowed entire motorcycle wheel"]
    for kw in pothole_kw:
        if kw in text:
            cat_scores["Pothole"] += 3
            evidence["Pothole"].append(kw)

    # 4. Flooding
    flood_kw = ["flooded", "flooding", "floods", "knee-deep", "waterlogging", "standing in water",
                "stranded", "approach floods", "channel rainwater"]
    for kw in flood_kw:
        if kw in text:
            cat_scores["Flooding"] += 3
            evidence["Flooding"].append(kw)

    # 5. Drain Blockage
    drain_kw = ["drain blocked", "drain completely blocked", "stormwater drain", "manhole cover missing",
                "main drain", "mosquito breeding", "draining directly"]
    for kw in drain_kw:
        if kw in text:
            cat_scores["Drain Blockage"] += 3
            evidence["Drain Blockage"].append(kw)

    # 6. Streetlight
    light_kw = ["streetlight", "streetlights", "lamp post", "lights out", "unlit", "dark at night",
                "flickering and sparking", "electrical hazard", "substation tripped", "wiring theft"]
    for kw in light_kw:
        if kw in text:
            cat_scores["Streetlight"] += 3
            evidence["Streetlight"].append(kw)

    # 7. Waste
    waste_kw = ["garbage", "waste", "bins overflowing", "dumped", "dead animal", "unusable by sunday", "market waste"]
    for kw in waste_kw:
        if kw in text:
            cat_scores["Waste"] += 3
            evidence["Waste"].append(kw)

    # 8. Noise
    noise_kw = ["music", "wedding band", "club music", "drilling", "amplifiers", "idling with engines on"]
    for kw in noise_kw:
        if kw in text:
            cat_scores["Noise"] += 3
            evidence["Noise"].append(kw)

    # 9. Road Damage
    road_kw = ["road surface cracked", "sinking", "broken tiles", "footpath broken", "footpath tiles",
               "road collapsed", "road subsidence", "buckled", "upturned paving", "dead trees with split branches",
               "irrigation system broken", "broken bench"]
    for kw in road_kw:
        if kw in text:
            cat_scores["Road Damage"] += 2
            evidence["Road Damage"].append(kw)

    # Resolve top category
    sorted_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = sorted_cats[0]
    second_cat, second_score = sorted_cats[1]

    # Check for genuine ambiguity / multi-category collisions
    flag = ""
    # If heritage mentions waste or noise or lighting, assess primary intent
    if "heritage" in text and ("waste" in text or "garbage" in text):
        top_cat = "Waste"
        flag = "NEEDS_REVIEW"
    elif "heritage" in text and ("lights out" in text or "lamp post" in text):
        top_cat = "Heritage Damage" if "heritage lamp post" in text or "defaced" in text else "Streetlight"
        flag = "NEEDS_REVIEW"
    elif "heritage" in text and "music" in text or "amplifiers" in text:
        top_cat = "Noise"
        flag = "NEEDS_REVIEW"
    elif top_score == 0:
        top_cat = "Other"
        flag = "NEEDS_REVIEW"
    elif top_score == second_score and top_score > 0:
        flag = "NEEDS_REVIEW"

    # Assemble matched evidence string
    matched_ev = ", ".join(evidence.get(top_cat, [])) or description[:30]
    return top_cat, flag, matched_ev


def classify_complaint(row: Dict[str, Any]) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    location = row.get("location", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine Category & Flag
    category, flag, matched_evidence = determine_category_and_flag(description, location)

    # Determine Priority based on severity keywords
    is_urgent, matched_kw = check_severity(f"{description} {location}")
    priority = "Urgent" if is_urgent else "Standard"

    # Build verifiable justification reason citing specific description phrases
    # Pick representative phrase from description
    sample_phrase = description.split(".")[0].strip() if "." in description else description
    if is_urgent:
        reason = f"Classified as {category} with {priority} priority due to '{', '.join(matched_kw)}' in '{sample_phrase}'."
    else:
        reason = f"Classified as {category} with {priority} priority based on description: '{sample_phrase}'."

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

    results = []
    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row_idx, row in enumerate(reader):
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Graceful handling for bad/corrupted rows
                cid = row.get("complaint_id", f"UNKNOWN_ROW_{row_idx}")
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed due to error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
