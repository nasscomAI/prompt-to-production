"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, List

# Allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords for Urgent priority
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def get_semantic_tag_cloud(description: str) -> List[dict]:
    """
    Generates a machine-readable semantic representation (tag cloud) for the description.
    This acts as the intermediate semantic layer before applying deterministic decision rules.
    """
    tag_cloud = []
    desc_lower = description.lower()

    # 1. Pothole terms
    if "pothole" in desc_lower or "crater" in desc_lower:
        tag_cloud.append({
            "term": "pothole" if "pothole" in desc_lower else "crater",
            "normalized_term": "pothole",
            "semantic_type": "infrastructure_problem",
            "context": "road_maintenance",
            "category_relevance": "Pothole",
            "priority_relevance": "Standard",
            "safety_relevance": "Medium",
            "confidence": 0.95,
            "related_terms": ["road", "hole", "street"]
        })

    # 2. Flooding terms
    if any(k in desc_lower for k in ["flood", "flooded", "flooding", "water", "rainwater"]):
        tag_cloud.append({
            "term": [k for k in ["flooded", "flooding", "flood", "water", "rainwater"] if k in desc_lower][0],
            "normalized_term": "flooding",
            "semantic_type": "natural_hazard",
            "context": "civic_infrastructure",
            "category_relevance": "Flooding",
            "priority_relevance": "Standard",
            "safety_relevance": "High",
            "confidence": 0.90,
            "related_terms": ["rain", "stormwater", "underpass"]
        })

    # 3. Drain Blockage terms
    if "drain" in desc_lower or "drainage" in desc_lower or "draining" in desc_lower:
        tag_cloud.append({
            "term": "drain",
            "normalized_term": "drainage",
            "semantic_type": "drainage_system",
            "context": "civic_infrastructure",
            "category_relevance": "Drain Blockage",
            "priority_relevance": "Standard",
            "safety_relevance": "Medium",
            "confidence": 0.90,
            "related_terms": ["blockage", "debris", "overflow"]
        })

    # 4. Streetlight terms
    if any(k in desc_lower for k in ["streetlight", "streetlights", "unlit", "darkness", "lights out", "lamp post"]):
        term_found = [k for k in ["streetlight", "streetlights", "unlit", "darkness", "lights out", "lamp post"] if k in desc_lower][0]
        tag_cloud.append({
            "term": term_found,
            "normalized_term": "streetlight",
            "semantic_type": "utility_problem",
            "context": "public_safety",
            "category_relevance": "Streetlight",
            "priority_relevance": "Standard",
            "safety_relevance": "Medium",
            "confidence": 0.95,
            "related_terms": ["lights", "power", "dark"]
        })

    # 5. Waste terms
    if any(k in desc_lower for k in ["garbage", "waste", "dead animal", "bins", "dumped", "trash"]):
        term_found = [k for k in ["garbage", "waste", "dead animal", "bins", "dumped", "trash"] if k in desc_lower][0]
        tag_cloud.append({
            "term": term_found,
            "normalized_term": "waste",
            "semantic_type": "sanitation_problem",
            "context": "public_health",
            "category_relevance": "Waste",
            "priority_relevance": "Standard",
            "safety_relevance": "Medium",
            "confidence": 0.90,
            "related_terms": ["overflowing", "refuse", "debris"]
        })

    # 6. Noise terms
    if any(k in desc_lower for k in ["music", "drilling", "wedding", "noise", "past midnight", "amplifiers", "idling", "engines"]):
        term_found = [k for k in ["music", "drilling", "wedding", "noise", "past midnight", "amplifiers", "idling", "engines"] if k in desc_lower][0]
        tag_cloud.append({
            "term": term_found,
            "normalized_term": "noise",
            "semantic_type": "nuisance",
            "context": "residential_comfort",
            "category_relevance": "Noise",
            "priority_relevance": "Low",
            "safety_relevance": "Low",
            "confidence": 0.95,
            "related_terms": ["loud", "audible", "disturbance"]
        })

    # 7. Heritage terms
    if any(k in desc_lower for k in ["heritage", "historic", "museum", "ancient", "step well", "heritage stone"]):
        term_found = [k for k in ["heritage", "historic", "museum", "ancient", "step well", "heritage stone"] if k in desc_lower][0]
        tag_cloud.append({
            "term": term_found,
            "normalized_term": "heritage",
            "semantic_type": "cultural_heritage",
            "context": "preservation",
            "category_relevance": "Heritage Damage",
            "priority_relevance": "Standard",
            "safety_relevance": "Low",
            "confidence": 0.95,
            "related_terms": ["monument", "historic_site", "precinct"]
        })

    # 8. Heat Hazard terms
    if any(k in desc_lower for k in ["melting", "temperature", "heatwave", "bubbling", "burns on contact", "heat", "sun", "44°c", "45°c", "52°c"]):
        term_found = [k for k in ["melting", "temperature", "heatwave", "bubbling", "burns on contact", "heat", "sun", "44°c", "45°c", "52°c"] if k in desc_lower][0]
        tag_cloud.append({
            "term": term_found,
            "normalized_term": "heat_hazard",
            "semantic_type": "environmental_hazard",
            "context": "public_safety",
            "category_relevance": "Heat Hazard",
            "priority_relevance": "Urgent",
            "safety_relevance": "High",
            "confidence": 0.90,
            "related_terms": ["thermal", "hot", "sunstroke"]
        })

    # 9. Road Damage terms
    if any(k in desc_lower for k in ["road surface", "collapsed", "subsidence", "buckled", "footpath", "tiles", "sinking", "paving", "broken paving", "manhole", "bridge", "subsided"]):
        term_found = [k for k in ["road surface", "collapsed", "subsidence", "buckled", "footpath", "tiles", "sinking", "paving", "broken paving", "manhole", "bridge", "subsided"] if k in desc_lower][0]
        tag_cloud.append({
            "term": term_found,
            "normalized_term": "road_damage",
            "semantic_type": "infrastructure_problem",
            "context": "road_safety",
            "category_relevance": "Road Damage",
            "priority_relevance": "Standard",
            "safety_relevance": "Medium",
            "confidence": 0.90,
            "related_terms": ["concrete", "tarmac", "pavement"]
        })

    return tag_cloud

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()
    tag_cloud = get_semantic_tag_cloud(desc)

    # Deterministic category mapping based on prioritized keyword rules
    # Prioritise categories in order of specificity for these files:
    # 1. Heritage Damage (if explicitly containing heritage keywords, e.g. heritage, historic, ancient, museum)
    # 2. Heat Hazard (if explicitly environment/heat related, e.g. melting, temperature, sun, 44°C etc.)
    # 3. Pothole
    # 4. Flooding (must have explicit flooded, floods, rain, water)
    # 5. Drain Blockage (must mention drain)
    # 6. Streetlight
    # 7. Waste
    # 8. Noise
    # 9. Road Damage
    # 10. Other

    category = "Other"
    reason_term = ""

    # Check for Heritage first
    if any(k in desc_lower for k in ["heritage", "historic", "museum", "ancient", "step well", "heritage stone"]):
        category = "Heritage Damage"
        reason_term = [k for k in ["heritage", "historic", "museum", "ancient", "step well", "heritage stone"] if k in desc_lower][0]
    # Check for Heat Hazard
    elif any(k in desc_lower for k in ["melting", "temperature", "heatwave", "bubbling", "burns on contact", "heat", "sun", "44°c", "45°c", "52°c"]):
        category = "Heat Hazard"
        reason_term = [k for k in ["melting", "temperature", "heatwave", "bubbling", "burns on contact", "heat", "sun", "44°c", "45°c", "52°c"] if k in desc_lower][0]
    # Check for Pothole
    elif "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
        reason_term = "pothole" if "pothole" in desc_lower else "crater"
    # Check for Flooding (before Drain Blockage if both, e.g. "flooded... drain blocked")
    elif any(k in desc_lower for k in ["flooded", "flood", "floods", "rainwater"]):
        category = "Flooding"
        reason_term = [k for k in ["flooded", "flood", "floods", "rainwater"] if k in desc_lower][0]
    # Check for Drain Blockage
    elif any(k in desc_lower for k in ["drain blocked", "drainage", "stormwater drain", "drain"]):
        category = "Drain Blockage"
        reason_term = [k for k in ["drain blocked", "drainage", "stormwater drain", "drain"] if k in desc_lower][0]
    # Check for Streetlight
    elif any(k in desc_lower for k in ["streetlight", "streetlights", "unlit", "darkness", "lights out", "lamp post"]):
        category = "Streetlight"
        reason_term = [k for k in ["streetlight", "streetlights", "unlit", "darkness", "lights out", "lamp post"] if k in desc_lower][0]
    # Check for Waste
    elif any(k in desc_lower for k in ["garbage", "waste", "dead animal", "bins", "dumped", "trash"]):
        category = "Waste"
        reason_term = [k for k in ["garbage", "waste", "dead animal", "bins", "dumped", "trash"] if k in desc_lower][0]
    # Check for Noise
    elif any(k in desc_lower for k in ["music", "drilling", "wedding", "noise", "past midnight", "amplifiers", "idling", "engines"]):
        category = "Noise"
        reason_term = [k for k in ["music", "drilling", "wedding", "noise", "past midnight", "amplifiers", "idling", "engines"] if k in desc_lower][0]
    # Check for Road Damage
    elif any(k in desc_lower for k in ["road surface", "collapsed", "subsidence", "buckled", "footpath", "tiles", "sinking", "paving", "broken paving", "manhole", "bridge", "subsided"]):
        category = "Road Damage"
        reason_term = [k for k in ["road surface", "collapsed", "subsidence", "buckled", "footpath", "tiles", "sinking", "paving", "broken paving", "manhole", "bridge", "subsided"] if k in desc_lower][0]

    # Deterministic priority rules: independent of content flagging.
    # Severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    priority = "Standard"
    severity_matched = [w for w in SEVERITY_KEYWORDS if w in desc_lower]

    if severity_matched:
        priority = "Urgent"
        reason = f"Classified as {category} with Urgent priority because description contains severity indicator: '{severity_matched[0]}'."
    else:
        # Check days open or specific rules to determine Standard or Low
        days_open = int(row.get("days_open", 0)) if row.get("days_open") else 0
        if days_open >= 10:
            priority = "Standard"
        elif category in ["Noise", "Other"]:
            priority = "Low"
        else:
            priority = "Standard"

        reason_detail = f"mentioning '{reason_term}'" if reason_term else "and handled using rule-based classification"
        priority_detail = "with Standard priority due to operational turnaround times" if priority == "Standard" else "with Low priority"
        reason = f"Classified as {category} {priority_detail} based on keyword match {reason_detail}."

    # Ambiguity / safety flagging
    # Flag as NEEDS_REVIEW if category is genuinely ambiguous or extreme hazard (gas leak, dead tree etc.) is detected
    flag = ""
    if category == "Other" or "gas leak" in desc_lower or "dead trees" in desc_lower or "subsidence" in desc_lower or "collapsed" in desc_lower:
        flag = "NEEDS_REVIEW"
        reason += " Set flag to NEEDS_REVIEW due to potential safety or category ambiguity."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames if reader.fieldnames else []

            # Ensure we read rows even if some are corrupted or missing keys
            for line_no, row in enumerate(reader, start=1):
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Write dummy failure output to prevent crashing
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ERR-ROW-{line_no}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed to process row {line_no} due to error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        # Handle file read errors safely
        print(f"Error reading input CSV: {str(e)}")
        return

    # Write out output CSV
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        for res in results:
            writer.writerow(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
