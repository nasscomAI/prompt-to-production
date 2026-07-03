"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")
    
    # 1. Check for priority based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    desc_lower = description.lower()
    
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    # 2. Extract sentences to build the reason
    # A simple sentence splitter by punctuation
    import re
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', description) if s.strip()]
    
    # Find the specific sentence that triggers urgency if it is Urgent
    urgent_sentence = None
    if is_urgent:
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in severity_keywords):
                urgent_sentence = sentence
                break
                
    if is_urgent and urgent_sentence:
        reason = urgent_sentence
    else:
        reason = sentences[0] if sentences else description
        
    # Ensure reason ends with punctuation if it doesn't already
    if reason and not reason[-1] in ".!?":
        reason += "."
        
    # 3. Categorize based on keywords
    category = "Other"
    flag = ""
    
    has_pothole = "pothole" in desc_lower
    has_flood = "flood" in desc_lower
    has_drain = "drain" in desc_lower
    has_light = any(kw in desc_lower for kw in ["streetlight", "lights out", "unlit", "lamp post"])
    has_waste = any(kw in desc_lower for kw in ["waste", "garbage", "dumped", "dead animal", "refuse"])
    has_noise = any(kw in desc_lower for kw in ["noise", "music", "drilling", "amplifier"])
    has_road = any(kw in desc_lower for kw in ["road surface", "sinking", "footpath", "collapsed", "divider", "paving"])
    has_heritage = "heritage" in desc_lower
    has_heat = any(kw in desc_lower for kw in ["heat", "temperature", "melting", "burns", "sun", "heatwave"])
    
    # Check indicators
    active_indicators = [
        has_pothole, has_flood, has_drain, has_light, 
        has_waste, has_noise, has_road, has_heritage, has_heat
    ]
    trigger_count = sum(1 for ind in active_indicators if ind)
    
    if trigger_count > 1 or trigger_count == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        if has_pothole:
            category = "Pothole"
        elif has_flood:
            category = "Flooding"
        elif has_drain:
            category = "Drain Blockage"
        elif has_light:
            category = "Streetlight"
        elif has_waste:
            category = "Waste"
        elif has_noise:
            category = "Noise"
        elif has_road:
            category = "Road Damage"
        elif has_heritage:
            category = "Heritage Damage"
        elif has_heat:
            category = "Heat Hazard"
            
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
    results = []
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id')}: {e}")
                # Append a fallback row instead of crashing
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Failed to classify row.",
                    "flag": "NEEDS_REVIEW"
                })
                
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
