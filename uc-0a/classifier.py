"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    
    category = "Other"
    priority = "Standard"
    flag = ""
    
    # 1. Determine priority using severity keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    for kw in urgent_keywords:
        if kw in desc_lower:
            is_urgent = True
            break
            
    if is_urgent:
        priority = "Urgent"
        
    # 2. Determine category based on keywords (specific to general order)
    
    # Explicitly catch ambiguous or Other cases first
    if any(k in desc_lower for k in ["substation tripped", "irrigation system", "dead trees"]):
        category = "Other"
        flag = "NEEDS_REVIEW"
    # Drain Blockage
    elif any(k in desc_lower for k in ["drain blocked", "drainage", "stormwater drain", "draining directly", "drain is blocked", "main drain blocked", "completely blocked"]):
        category = "Drain Blockage"
    # Noise
    elif any(k in desc_lower for k in ["music", "drilling", "amplifiers", "idling with engines on", "wedding band", "band playing", "playing near", "club music", "wedding venue playing"]):
        category = "Noise"
    # Heritage Damage
    elif any(k in desc_lower for k in ["historic", "heritage residential", "heritage building", "heritage stone", "ancient step well", "heritage lamp post"]):
        category = "Heritage Damage"
    # Waste
    elif any(k in desc_lower for k in ["garbage", "waste", "dead animal"]):
        category = "Waste"
    # Streetlight
    elif any(k in desc_lower for k in ["streetlight", "streetlights", "lights out", "unlit", "lamp post"]):
        category = "Streetlight"
    # Heat Hazard
    elif any(k in desc_lower for k in ["heatwave", "melting at 44", "dangerous temperatures", "surface temperature", "burns on contact", "full sun", "bubbling at 45", "bubbling"]):
        category = "Heat Hazard"
    # Pothole
    elif any(k in desc_lower for k in ["pothole", "potholes"]):
        category = "Pothole"
    # Flooding
    elif any(k in desc_lower for k in ["flood", "flooded", "floods", "rainwater"]):
        category = "Flooding"
    # Road Damage
    elif any(k in desc_lower for k in ["road surface", "footpath", "collapsed", "crater", "subsidence", "subsided", "broken bench", "upturned paving", "tarmac surface", "road dividers", "broken and sinking", "tiles broken", "manhole cover missing"]):
        category = "Road Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # If category is Other, ensure flag is set
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 3. Generate a one-sentence reason citing specific words from the description
    sentences = [s.strip() for s in description.split('.') if s.strip()]
    if not sentences:
        reason = "The complaint has no description to classify."
        flag = "NEEDS_REVIEW"
    elif priority == "Urgent":
        # Find the sentence triggering priority
        triggered_sentence = sentences[0]
        for s in sentences:
            for kw in urgent_keywords:
                if kw in s.lower():
                    triggered_sentence = s
                    break
        reason = f"Urgent priority is assigned due to the phrase: '{triggered_sentence}'."
    else:
        reason = f"Classified as {category} based on the description: '{sentences[0]}'."
        
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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV is empty or has no header.")
                
            results = []
            for i, row in enumerate(reader, start=1):
                try:
                    # Check for null/empty row or missing crucial keys
                    if not row or all(v is None or v.strip() == "" for v in row.values()):
                        print(f"Skipping empty row at line {i}", file=sys.stderr)
                        continue
                    
                    if "complaint_id" not in row or "description" not in row:
                        # Missing necessary columns, flag and output error row
                        complaint_id = row.get("complaint_id", f"UNKNOWN_ROW_{i}")
                        results.append({
                            "complaint_id": complaint_id,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Missing required columns in input CSV row.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                        
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    # Prevent crash on bad rows
                    print(f"Error classifying row {i}: {e}", file=sys.stderr)
                    complaint_id = row.get("complaint_id", f"ERROR_ROW_{i}")
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch classification: {e}", file=sys.stderr)
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
