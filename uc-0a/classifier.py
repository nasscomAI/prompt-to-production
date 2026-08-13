"""
UC-0A — Complaint Classifier
Implemented using a robust, rule-based classification engine.
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
    desc = row.get("description", "").strip()
    comp_id = row.get("complaint_id", "").strip()
    
    if not desc:
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = desc.lower()
    
    # Category Classification rules
    category = "Other"
    flag = ""
    
    # Order of matching is important to avoid misclassification
    if "pothole" in desc_lower:
        category = "Pothole"
    elif " streetlight" in desc_lower or "streetlight" in desc_lower or " lights out" in desc_lower or "lamp post" in desc_lower:
        category = "Streetlight"
    elif "heritage" in desc_lower or "ancient" in desc_lower or "historic" in desc_lower or "museum" in desc_lower:
        # Note: If it's just streetlights out on a heritage street, check if heritage damage is primary
        if "lights out" in desc_lower or "lamp post" in desc_lower:
            # Let's decide based on whether there is actual physical damage to heritage
            if "knocked over" in desc_lower or "defaced" in desc_lower or "stone not replaced" in desc_lower:
                category = "Heritage Damage"
            else:
                category = "Streetlight"
        elif "waste" in desc_lower or "garbage" in desc_lower:
            category = "Waste"
        elif "music" in desc_lower or "amplifier" in desc_lower:
            category = "Noise"
        else:
            category = "Heritage Damage"
    elif "drain" in desc_lower or "manhole" in desc_lower or "sewer" in desc_lower:
        category = "Drain Blockage"
    elif "flooded" in desc_lower or "floods" in desc_lower or "rainwater" in desc_lower:
        category = "Flooding"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dumped" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower or "drilling" in desc_lower or "sound" in desc_lower or "audible" in desc_lower:
        category = "Noise"
    elif "melting" in desc_lower or "temperature" in desc_lower or "heatwave" in desc_lower or "heat" in desc_lower or "sun" in desc_lower:
        category = "Heat Hazard"
    elif "road" in desc_lower or "paving" in desc_lower or "footpath" in desc_lower or "bridge" in desc_lower or "tarmac" in desc_lower or "sidewalk" in desc_lower or "surface" in desc_lower or "tiles broken" in desc_lower:
        category = "Road Damage"
    
    # Priority classification rules based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    matched_severity = []
    for word in severity_keywords:
        if re.search(r'\b' + re.escape(word) + r'\w*', desc_lower):
            is_urgent = True
            matched_severity.append(word)
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # Constructing a concise reason citing specific words
    if is_urgent:
        reason = f"Urgent priority assigned due to safety-critical keyword(s) '{', '.join(matched_severity)}' in description."
    else:
        # standard fallback citation
        reason = f"Classified as {category} based on description details."
        
    # Let's ensure the reason is a single sentence and cites specific words
    # Let's cite the exact matching words for category as well
    if category != "Other":
        words_found = []
        for keyword in ["pothole", "flood", "drain", "streetlight", "garbage", "waste", "music", "noise", "road", "footpath", "heritage", "ancient", "heat", "temperature", "manhole", "animal", "melting", "temp", "hot", "sun", "burn", "dark", "sparking", "flickering", "drilling", "audible", "amplifier", "tram", "cobblestones", "museum", "historic", "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]:
            if keyword in desc_lower:
                words_found.append(keyword)
        reason = f"Classified as {category} citing '{', '.join(words_found)}' from: \"{desc[:60]}...\""
    else:
        reason = f"Classified as Other due to lack of distinct category keywords in description: \"{desc[:60]}...\""
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": comp_id,
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
        print(f"Error: Input file {input_path} does not exist.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        for row in reader:
            try:
                classified = classify_complaint(row)
                # Merge original row fields with classification result
                output_row = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": classified["category"],
                    "priority": classified["priority"],
                    "reason": classified["reason"],
                    "flag": classified["flag"]
                }
                results.append(output_row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id')}: {e}")
                
    # Define output fields
    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
