"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Allowed categories from schema
CATEGORIES = [
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

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    matches = []
    
    # 1. Pothole
    if "pothole" in desc:
        matches.append("Pothole")
    
    # 2. Flooding / Drain Blockage
    is_flooding = any(x in desc for x in ["flood", "waterlog", "rainwater", "standing in water", "flooding"])
    is_drain = any(x in desc for x in ["drain", "sewer", "manhole", "drainage"])
    
    if is_flooding:
        matches.append("Flooding")
    if is_drain:
        matches.append("Drain Blockage")
        
    # 3. Streetlight
    if any(x in desc for x in ["streetlight", "unlit", "darkness", "lights out", "lamp post"]):
        matches.append("Streetlight")
        
    # 4. Waste
    if any(x in desc for x in ["waste", "garbage", "trash", "bin", "refuse", "dumped", "dead animal", "animal"]):
        matches.append("Waste")
        
    # 5. Noise
    if any(x in desc for x in ["noise", "music", "loud", "audible", "amplifier", "drilling", "wedding venue", "wedding band", "idling"]):
        matches.append("Noise")
        
    # 6. Heritage Damage
    if any(x in desc for x in ["heritage", "historic", "ancient", "museum", "monument", "step well", "bow barracks"]):
        matches.append("Heritage Damage")
        
    # 7. Heat Hazard
    if any(x in desc for x in ["heat", "temperature", "melting", "bubbling", "hot", "sun", "burns", "44°c", "45°c", "52°c"]):
        matches.append("Heat Hazard")
        
    # 8. Road Damage
    if any(x in desc for x in ["road surface", "road collapsed", "road subsidence", "cracked and sinking", "footpath", "pavement", "tiles broken", "paving", "bridge approach", "collapsed", "tarmac"]):
        matches.append("Road Damage")

    unique_matches = []
    for m in matches:
        if m not in unique_matches:
            unique_matches.append(m)
            
    flag = ""
    category = "Other"
    
    if len(unique_matches) > 1:
        category = unique_matches[0]
        # Ambiguity resolution/refinement
        if "Heritage Damage" in unique_matches:
            if any(x in desc for x in ["garbage", "waste"]):
                category = "Waste"
            elif any(x in desc for x in ["music", "band", "amplifier"]):
                category = "Noise"
            elif any(x in desc for x in ["lights out", "lamp post"]):
                category = "Heritage Damage"
            else:
                category = "Heritage Damage"
        elif "Drain Blockage" in unique_matches and "Flooding" in unique_matches:
            category = "Drain Blockage"
        
        flag = "NEEDS_REVIEW"
    elif len(unique_matches) == 1:
        category = unique_matches[0]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Priority
    priority = "Standard"
    if any(kw in desc for kw in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
        
    # Reason (one sentence citing specific words from the description)
    words = []
    for m in unique_matches:
        if m == "Pothole": words.append("pothole")
        elif m == "Flooding": words.append("flooded/rainwater")
        elif m == "Drain Blockage": words.append("drain/manhole")
        elif m == "Streetlight": words.append("lights/darkness")
        elif m == "Waste": words.append("garbage/waste")
        elif m == "Noise": words.append("music/noise")
        elif m == "Heritage Damage": words.append("heritage/historic")
        elif m == "Heat Hazard": words.append("heat/temperature")
        elif m == "Road Damage": words.append("road/footpath")
    
    sev_matched = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    
    citation_parts = []
    if words:
        citation_parts.append(f"category-related terms like '{words[0]}'")
    if sev_matched:
        citation_parts.append(f"severity keywords like '{sev_matched[0]}'")
        
    citation_str = " and ".join(citation_parts) if citation_parts else "relevant details"
    reason = f"Classified as {category} with {priority} priority citing {citation_str} from description."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
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
    
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Fallback to avoid crashing the entire batch
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing failed: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Ensure parent directories of output_path exist
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
