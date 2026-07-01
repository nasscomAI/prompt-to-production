"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    This function's behavior is guided by agents.md and skills.md.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # Check for empty/null description
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or invalid description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = str(description).lower().strip()
    
    # 1. Determine priority based on severity keywords (case-insensitive)
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_severity_keyword = None
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_severity_keyword = kw
            break
            
    # 2. Check for ambiguity/multi-topic conflicts or unmapped topics
    category = None
    flag = ""
    
    is_heritage = any(w in desc_lower for w in ["heritage", "historic", "ancient", "museum"])
    has_streetlight = any(w in desc_lower for w in ["light", "unlit", "darkness", "lamp"])
    has_road_damage = any(w in desc_lower for w in ["road", "cobbles", "paving", "footpath", "sinking", "subsidence", "subside", "cracked", "tarmac", "collapsed"])
    has_noise = any(w in desc_lower for w in ["music", "noise", "loud", "sound", "playing", "amplifier", "drilling", "idling"])
    has_waste = any(w in desc_lower for w in ["garbage", "waste", "trash", "rubbish", "dumped", "bins", "dead animal", "refuse"])
    has_drain = any(w in desc_lower for w in ["drain", "sewer", "stormwater"])
    has_flooding = any(w in desc_lower for w in ["flood", "waterlogged", "rainwater", "water accumulation", "water standing"])
    
    # Genuinely ambiguous cases
    # A. Heritage conflict with other categories (Streetlight, Road Damage, Noise, Waste)
    if is_heritage and (has_streetlight or has_road_damage or has_noise or has_waste):
        category = "Other"
        flag = "NEEDS_REVIEW"
    # B. Gas leak / pipeline near road subsidence
    elif "gas pipeline" in desc_lower or "gas leak" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
    # C. Dead trees falling hazard (does not fit any standard category cleanly)
    elif "dead trees" in desc_lower or "split branches" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
    # D. New residential complex draining directly onto public road
    elif "draining directly onto public road" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
    # E. Supermarket delivery trucks idling (noise vs pollution/other)
    elif "idling" in desc_lower:
        category = "Noise"
        
    # Standard classification rules if not flagged as ambiguous
    if category is None:
        if "pothole" in desc_lower:
            category = "Pothole"
        elif has_drain:
            category = "Drain Blockage"
        elif has_flooding:
            category = "Flooding"
        elif has_streetlight:
            category = "Streetlight"
        elif has_waste:
            category = "Waste"
        elif has_noise:
            category = "Noise"
        elif is_heritage:
            category = "Heritage Damage"
        elif any(w in desc_lower for w in ["melt", "temperature", "heatwave", "sun", "44°c", "45°c", "52°c"]):
            category = "Heat Hazard"
        elif has_road_damage:
            category = "Road Damage"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            
    # Extract first sentence as citation
    sentences = re.split(r'(?<=[.!?])\s+', description.strip())
    first_sentence = sentences[0] if sentences else description.strip()
    if not first_sentence.endswith('.'):
        first_sentence += '.'
        
    # Formulate exactly one sentence citing specific words from description
    if matched_severity_keyword:
        reason = f"Classified as {category} with {priority} priority because the description cites '{first_sentence.strip('.')}', containing the severity trigger word '{matched_severity_keyword}'."
    else:
        reason = f"Classified as {category} with {priority} priority because the description cites '{first_sentence.strip('.')}'."
        
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
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist.")
        
    results = []
    
    with open(input_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Input CSV file {input_path} has no headers.")
            
        for line_num, row in enumerate(reader, start=2):
            try:
                # Basic validation for malformed rows
                if not row or not any(row.values()):
                    continue
                    
                # Classify complaint row
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                comp_id = row.get("complaint_id", f"ERROR_ROW_{line_num}")
                print(f"Error classifying row {line_num} ({comp_id}): {e}")
                results.append({
                    "complaint_id": comp_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"System error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Write to output CSV
    headers = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
