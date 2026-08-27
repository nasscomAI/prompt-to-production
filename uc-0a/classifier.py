"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    desc = row.get("description", "").strip()
    
    # Default outputs
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is empty.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # 1. Determine priority based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = [kw for kw in severity_keywords if kw in desc_lower]
    
    if matched_severity:
        priority = "Urgent"
        
    # 2. Check for explicit ambiguity cases (multiple categories or other ambiguities)
    # Heritage + Other (Waste/Streetlight/Road Damage/Noise)
    is_heritage = "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower or "tagore museum" in desc_lower
    
    # Detect primary aspects
    import re
    has_pothole = "pothole" in desc_lower
    has_flooding = "flood" in desc_lower or "waterlogging" in desc_lower or "rainwater" in desc_lower
    has_streetlight = "streetlight" in desc_lower or "lights out" in desc_lower or "unlit" in desc_lower or "lamp post" in desc_lower or "darkness" in desc_lower
    has_waste = "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "dumped" in desc_lower or "dead animal" in desc_lower
    has_noise = any(kw in desc_lower for kw in ["music", "noise", "drilling", "idling", "amplifier", "playing", "band"])
    has_road_damage = "road surface" in desc_lower or "tarmac" in desc_lower or "paving" in desc_lower or "cobblestones" in desc_lower or "footpath" in desc_lower or "collapsed" in desc_lower or "subsidence" in desc_lower or "manhole cover" in desc_lower or "broken bench" in desc_lower
    has_heat = "melting" in desc_lower or "temperature" in desc_lower or "heatwave" in desc_lower or "bubbling" in desc_lower or "storing heat" in desc_lower or "full sun" in desc_lower
    has_drain = bool(re.search(r'\bdrains?\b', desc_lower))
    # Ambiguity checks
    if is_heritage and (has_streetlight or has_waste or has_road_damage or has_noise):
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"The description mentions heritage context along with another issue, making it ambiguous."
    elif has_drain and has_flooding:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"The description mentions both drainage issues and flooding, making it ambiguous."
    elif "theft" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"The description mentions theft, which is a security issue and ambiguous for public utility classification."
    elif "dead tree" in desc_lower or "dead trees" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Dead tree hazards do not map cleanly to any standard category."
    elif "glass broken" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Broken shelter glass does not map cleanly to any standard category."
    elif "gas leak" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Gas leak smell reports are hazardous and do not map cleanly to any standard category."
    else:
        # Single category matching
        if has_pothole:
            category = "Pothole"
            reason = f"The complaint reports a pothole in the description."
        elif has_drain:
            category = "Drain Blockage"
            reason = f"The description mentions a blocked or issue-prone drain."
        elif has_flooding:
            category = "Flooding"
            reason = f"The complaint reports flooding or water pooling."
        elif has_streetlight:
            category = "Streetlight"
            reason = f"The complaint reports an issue with streetlights or public lighting."
        elif has_waste:
            category = "Waste"
            reason = f"The complaint reports waste, garbage, or trash buildup."
        elif has_noise:
            category = "Noise"
            reason = f"The complaint reports noise or music disturbance."
        elif is_heritage:
            category = "Heritage Damage"
            reason = f"The complaint reports damage or issues at a heritage site."
        elif has_heat:
            category = "Heat Hazard"
            reason = f"The complaint reports extreme heat or heat-related safety hazards."
        elif has_road_damage:
            category = "Road Damage"
            reason = f"The complaint reports damage to the road surface or footpath."
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = f"The description does not match any of the standard categories."

    # Update reason to cite words if priority is Urgent
    if priority == "Urgent" and matched_severity:
        reason = reason.rstrip(".") + f" (Urgent priority triggered by: {', '.join(matched_severity)})."

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
        raise FileNotFoundError(f"Input file not found at {input_path}")
        
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Fallback record in case of failure
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing failed: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Write to output file
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) if os.path.dirname(output_path) else ".", exist_ok=True)
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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
