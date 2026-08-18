"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # 1. Determine priority using severity keywords
    priority = "Standard"
    severity_keywords = ['injury', 'injured', 'child', 'school', 'hospital', 'hospitalised', 'ambulance', 'fire', 'hazard', 'fell', 'collapse', 'collapsed']
    matched_severity = []
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_severity.append(kw)
            
    # 2. Determine category matches
    categories = []
    
    # Heritage Damage
    if any(kw in desc_lower for kw in ["heritage", "historic", "ancient"]):
        categories.append("Heritage Damage")
        
    # Pothole
    if "pothole" in desc_lower:
        categories.append("Pothole")
        
    # Flooding
    # If it has drain, it is more likely Drain Blockage than Flooding
    if any(kw in desc_lower for kw in ["flood", "rainwater", "water"]) and "drain" not in desc_lower:
        categories.append("Flooding")
        
    # Drain Blockage
    if any(kw in desc_lower for kw in ["drain", "sewer", "manhole"]):
        categories.append("Drain Blockage")
        
    # Streetlight
    if any(kw in desc_lower for kw in ["streetlight", "lamp post", "unlit", "darkness", "lights out"]):
        categories.append("Streetlight")
        
    # Waste
    if any(kw in desc_lower for kw in ["garbage", "waste", "dead animal", "dumped"]):
        categories.append("Waste")
        
    # Noise
    if any(kw in desc_lower for kw in ["music", "drilling", "amplifier", "idling", "noise", "loud"]):
        categories.append("Noise")
        
    # Road Damage
    if any(kw in desc_lower for kw in ["road surface", "footpath", "paving", "subsided", "cracked", "sinking", "collapsed"]) and "pothole" not in desc_lower:
        categories.append("Road Damage")
        
    # Heat Hazard
    # Avoid substring match of 'sun' in 'Sunday' by matching word boundaries
    if any(kw in desc_lower for kw in ["melting", "temperature", "heatwave", "bubbling", "heat", "44°c", "45°c", "52°c"]) or re.search(r"\bsun\b", desc_lower) or "full sun" in desc_lower:
        categories.append("Heat Hazard")
        
    # 3. Resolve category and flag
    flag = ""
    # Pothole overrides other general classifications (e.g. rainwater flooding)
    if "Pothole" in categories and len(categories) > 1:
        category = "Pothole"
    elif len(categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = categories[0]
        
    # 4. Construct citation reason
    citations = []
    all_kws = ["pothole", "flood", "rainwater", "water", "drain", "manhole", "streetlight", "lamp post", "unlit", "darkness", "lights out", "garbage", "waste", "dead animal", "dumped", "music", "drilling", "amplifier", "idling", "noise", "road surface", "footpath", "paving", "subsided", "cracked", "sinking", "collapsed", "melting", "temperature", "heatwave", "bubbling", "heat", "sun", "heritage", "historic", "ancient"]
    for kw in all_kws:
        if kw in desc_lower:
            citations.append(kw)
            
    if citations:
        reason = f"Classified as {category} due to description containing: '{', '.join(citations[:3])}'."
    else:
        snippet = desc[:40] + "..." if len(desc) > 40 else desc
        reason = f"Classified as {category} based on description: '{snippet}'."
        
    if priority == "Urgent" and matched_severity:
        reason += f" Priority set to Urgent due to severity keyword: '{matched_severity[0]}'."
        
    return {
        "complaint_id": row.get("complaint_id"),
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
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                # Do not crash on bad rows, produce output even if some rows fail
                print(f"Error classifying row {row.get('complaint_id')}: {e}")
                results.append({
                    "complaint_id": row.get("complaint_id"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Failed to classify due to error: {e}",
                    "flag": "NEEDS_REVIEW"
                })
                
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
