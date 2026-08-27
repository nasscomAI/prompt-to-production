"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, Tuple

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
    "injury", "injured",
    "child", "children",
    "school",
    "hospital", "hospitalised", "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "fell", "fall",
    "collapse", "collapsed"
]


def determine_category(desc: str) -> Tuple[str, str]:
    """
    Determines category and key phrase evidence from the complaint description.
    Returns (category_name, evidence_keyword).
    """
    desc_lower = desc.lower()

    # 1. Pothole
    if "pothole" in desc_lower or "crater" in desc_lower:
        kw = "pothole" if "pothole" in desc_lower else "crater"
        return "Pothole", kw

    # 2. Flooding
    if any(k in desc_lower for k in ["flooded", "floods", "flooding", "waterlogging", "inundated", "submerged", "rainwater through main road"]):
        for k in ["flooded", "floods", "flooding", "waterlogging", "inundated", "submerged"]:
            if k in desc_lower:
                return "Flooding", k
        return "Flooding", "flooding"

    # 3. Heritage Damage
    if any(k in desc_lower for k in ["heritage", "historic", "ancient step well", "monument", "tagore museum"]):
        if "garbage" in desc_lower or "waste" in desc_lower:
            return "Waste", "garbage in heritage zone"
        if "music" in desc_lower or "amplifiers" in desc_lower or "band" in desc_lower:
            return "Noise", "noise in heritage precinct"
        if "lights out" in desc_lower or "light post" in desc_lower:
            if "lamp post" in desc_lower or "heritage stone" in desc_lower or "defaced" in desc_lower:
                return "Heritage Damage", "heritage lamp post"
            return "Streetlight", "lights out"
        return "Heritage Damage", "heritage concern"

    # 4. Drain Blockage
    if "manhole" in desc_lower or "stormwater drain" in desc_lower or ("drain" in desc_lower and "block" in desc_lower):
        if "manhole" in desc_lower:
            return "Drain Blockage", "manhole cover"
        return "Drain Blockage", "drain blocked"

    # 5. Streetlight
    if any(k in desc_lower for k in ["streetlight", "streetlights", "lamp post", "unlit", "darkness", "lights out", "wiring theft", "substation tripped"]):
        for k in ["streetlight", "streetlights", "lamp post", "unlit", "darkness", "lights out", "wiring theft", "substation tripped"]:
            if k in desc_lower:
                return "Streetlight", k
        return "Streetlight", "lighting issue"

    # 6. Waste
    if any(k in desc_lower for k in ["garbage", "waste", "dumped", "dead animal", "overflowing", "debris"]):
        for k in ["garbage", "waste", "dumped", "dead animal", "overflowing"]:
            if k in desc_lower:
                return "Waste", k
        return "Waste", "waste issue"

    # 7. Noise
    if any(k in desc_lower for k in ["music", "drilling", "amplifiers", "idling", "audible", "loud"]):
        for k in ["music", "drilling", "amplifiers", "idling", "audible"]:
            if k in desc_lower:
                return "Noise", k
        return "Noise", "noise issue"

    # 8. Heat Hazard
    if any(k in desc_lower for k in ["heat", "heatwave", "44°c", "45°c", "52°c", "temperature", "melting", "full sun", "burns"]):
        for k in ["melting", "heatwave", "temperature", "burns", "full sun", "heat"]:
            if k in desc_lower:
                return "Heat Hazard", k
        return "Heat Hazard", "heat issue"

    # 9. Road Damage
    if any(k in desc_lower for k in ["footpath", "road surface", "tarmac", "road collapsed", "subsidence", "subsided", "buckled", "tiles broken", "cracked", "paving"]):
        for k in ["footpath", "road surface", "road collapsed", "subsidence", "subsided", "buckled", "tiles broken", "cracked", "paving"]:
            if k in desc_lower:
                return "Road Damage", k
        return "Road Damage", "road damage"

    # Fallback / Ambiguous -> Other
    return "Other", ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip() if row.get("description") else ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Complaint description missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    category, evidence_kw = determine_category(description)

    # Priority determination based on severity keywords
    desc_lower = description.lower()
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower and kw not in matched_severity:
            matched_severity.append(kw)

    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Flag and Refusal handling
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Category could not be determined conclusively from description alone."
    else:
        flag = ""
        if matched_severity:
            reason = f"Citing '{evidence_kw}' from description and severity trigger word(s): {', '.join(matched_severity)}."
        else:
            reason = f"Citing '{evidence_kw}' from description."

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
    Flags nulls/bad rows, does not crash, produces output even if some rows fail.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

