"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def extract_reason(desc: str, category: str, priority: str) -> str:
    """
    Helper function to extract a single sentence citing specific words from the description
    that justify the classification.
    """
    sentences = [s.strip() for s in re.split(r'\.|\?|!', desc) if s.strip()]
    if not sentences:
        return desc
    
    # Define keywords associated with each category
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rain", "water", "underpass"],
        "Drain Blockage": ["drain", "block", "debris"],
        "Streetlight": ["streetlight", "light", "lamp", "unlit", "darkness", "substation"],
        "Waste": ["garbage", "waste", "animal", "bin", "refuse", "dumped"],
        "Noise": ["music", "noise", "loud", "sound", "amplifier", "drill", "idling", "engine"],
        "Road Damage": ["crack", "sink", "subsid", "collaps", "buckl", "broken", "manhole", "paving", "divider", "crater"],
        "Heritage Damage": ["heritage", "historic", "ancient"],
        "Heat Hazard": ["melt", "heat", "temperature", "burn", "heatwave", "sun", "hot"]
    }
    
    keywords = list(category_keywords.get(category, []))
    if priority == "Urgent":
        keywords.extend(["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"])
        
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(kw in s_lower for kw in keywords):
            return sentence + "."
            
    # Default to first sentence if no keyword matches
    return sentences[0] + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    
    # Initialize output values
    category = "Other"
    priority = "Standard"
    reason = "Required fields are missing."
    flag = ""
    
    # Check for empty/missing/null fields in the row
    is_null_present = False
    for k, v in row.items():
        if v is None or str(v).strip() == "":
            is_null_present = True
            break
            
    if not complaint_id or not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": reason,
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    matches = []
    
    # 1. Pothole
    if "pothole" in desc_lower:
        matches.append("Pothole")
        
    # 2. Drain Blockage
    if "drain" in desc_lower and any(w in desc_lower for w in ["block", "debris"]):
        matches.append("Drain Blockage")
        
    # 3. Flooding
    if any(w in desc_lower for w in ["flood", "rain", "water", "underpass"]):
        matches.append("Flooding")
        
    # 4. Streetlight
    if any(w in desc_lower for w in ["streetlight", "light", "lamp", "unlit", "darkness", "substation"]):
        matches.append("Streetlight")
        
    # 5. Waste
    if any(w in desc_lower for w in ["garbage", "waste", "animal", "bin", "refuse", "dumped"]):
        matches.append("Waste")
        
    # 6. Noise
    if any(w in desc_lower for w in ["music", "noise", "loud", "sound", "amplifier", "drill", "idling", "engine"]):
        matches.append("Noise")
        
    # 7. Road Damage
    if any(w in desc_lower for w in ["crack", "sink", "subsid", "collaps", "buckl", "broken", "manhole", "paving", "divider", "crater"]):
        matches.append("Road Damage")
        
    # 8. Heritage Damage
    if any(w in desc_lower for w in ["heritage", "historic", "ancient"]):
        matches.append("Heritage Damage")
        
    # 9. Heat Hazard
    if any(w in desc_lower for w in ["melt", "heat", "temperature", "burn", "heatwave", "sun", "hot"]):
        matches.append("Heat Hazard")
        
    # Determine primary category and flag ambiguity
    if not matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matches) == 1:
        category = matches[0]
        flag = ""
    else:
        # Ambiguous category! Set NEEDS_REVIEW.
        # Prefer specific matches in sorted order
        priority_order = ["Pothole", "Drain Blockage", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard"]
        matches_sorted = sorted(matches, key=lambda x: priority_order.index(x) if x in priority_order else 99)
        category = matches_sorted[0]
        flag = "NEEDS_REVIEW"
        
    # If specific safety/system level ambiguity triggers are met:
    if "gas leak" in desc_lower or "substation tripped" in desc_lower:
        flag = "NEEDS_REVIEW"
        
    if is_null_present:
        flag = "NEEDS_REVIEW"
        
    # Priority rules
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(kw in desc_lower for kw in severity_keywords):
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"
        
    # Reason generation
    reason = extract_reason(desc, category, priority)
    
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
        with open(input_path, mode='r', encoding='utf-8', errors='ignore') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row: {row}. Error: {e}")
                    comp_id = row.get("complaint_id", "UNKNOWN").strip()
                    results.append({
                        "complaint_id": comp_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Fatal error reading input file {input_path}: {e}")
        raise e
        
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Fatal error writing output file {output_path}: {e}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

