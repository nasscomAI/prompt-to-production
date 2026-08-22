"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not row:
        return {
            "complaint_id": "UNKNOWN",
            "category": "Other",
            "priority": "Low",
            "reason": "Empty row or null input provided.",
            "flag": "NEEDS_REVIEW"
        }

    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    if description is None:
        description = ""
    description = str(description).strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Check severity keywords for priority
    # Keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = [kw for kw in severity_keywords if kw in desc_lower]
    
    priority = "Urgent" if matched_severity else "Standard"
    
    matched_categories = []
    
    # Category checks
    # Pothole
    if "pothole" in desc_lower:
        matched_categories.append("Pothole")
    
    # Flooding
    if any(k in desc_lower for k in ["flood", "flooding", "flooded", "rainwater", "draining directly"]):
        matched_categories.append("Flooding")
        
    # Streetlight
    if any(k in desc_lower for k in ["streetlight", "lights out", "unlit", "lamp post", "substation tripped", "darkness"]):
        matched_categories.append("Streetlight")
        
    # Waste
    if any(k in desc_lower for k in ["garbage", "waste", "dead animal", "bins overflowing"]):
        matched_categories.append("Waste")
        
    # Noise
    if any(k in desc_lower for k in ["music", "audible", "noise", "amplifier", "amplifiers", "wedding band", "drilling", "engines on"]):
        matched_categories.append("Noise")
        
    # Road Damage
    if any(k in desc_lower for k in ["paving", "pavement", "cracked", "sinking", "subsided", "buckled", "tiles", "collapsed", "subsidence", "manhole", "crater", "footpath", "cobblestones"]):
        matched_categories.append("Road Damage")
        
    # Heritage Damage
    if any(k in desc_lower for k in ["heritage", "ancient", "museum", "historic"]):
        matched_categories.append("Heritage Damage")
        
    # Heat Hazard
    if any(k in desc_lower for k in ["melting", "temperature", "heatwave", "heat.", "storing heat", "full sun", "52°c", "44°c", "45°c", "temperature"]):
        matched_categories.append("Heat Hazard")
        
    # Drain Blockage
    if any(k in desc_lower for k in ["drain blocked", "drainage blocked", "stormwater drain", "main drain", "drain completely blocked"]):
        matched_categories.append("Drain Blockage")

    flag = ""
    # Disambiguation logic
    if len(matched_categories) > 1:
        flag = "NEEDS_REVIEW"
        if "Heritage Damage" in matched_categories:
            other_cats = [c for c in matched_categories if c != "Heritage Damage"]
            category = other_cats[0]
        elif "Flooding" in matched_categories and "Drain Blockage" in matched_categories:
            category = "Drain Blockage"
        else:
            category = matched_categories[0]
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Construct the reason sentence.
    sentences = re.split(r'[.!?]+', description)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Try to find a sentence citing category trigger
    category_kws = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rainwater", "draining"],
        "Streetlight": ["streetlight", "light", "unlit", "darkness", "substation"],
        "Waste": ["garbage", "waste", "animal", "bin"],
        "Noise": ["music", "noise", "audible", "amplifier", "drilling", "engine"],
        "Road Damage": ["paving", "surface", "crack", "sink", "buckle", "collapsed", "subsidence", "manhole", "crater", "tiles"],
        "Heritage Damage": ["heritage", "ancient", "museum", "historic"],
        "Heat Hazard": ["melting", "temperature", "heatwave", "heat", "sun", "burn"],
        "Drain Blockage": ["drain"]
    }
    
    cite_sentence = ""
    kws = category_kws.get(category, [])
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in kws):
            cite_sentence = s
            break
    if not cite_sentence and sentences:
        cite_sentence = sentences[0]
    if not cite_sentence:
        cite_sentence = description
        
    # Standardize output format
    if priority == "Urgent":
        reason = f"Classified as {category} with Urgent priority because description cites '{cite_sentence}' containing '{matched_severity[0]}'."
    else:
        reason = f"Classified as {category} because description cites '{cite_sentence}'."

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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or has no headers.")
            
            for line_no, row in enumerate(reader, start=2):
                try:
                    if not row:
                        results.append({
                            "complaint_id": f"ERROR-ROW-{line_no}",
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Empty row in input CSV.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                    
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as row_err:
                    complaint_id = row.get("complaint_id", f"ERROR-ROW-{line_no}") if row else f"ERROR-ROW-{line_no}"
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed to process row: {str(row_err)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as file_err:
        print(f"Error reading input file {input_path}: {file_err}")
        return

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
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
