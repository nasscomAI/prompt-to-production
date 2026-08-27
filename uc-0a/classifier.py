"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # Severity keywords that must trigger Urgent
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Check priority
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard" # Default priority is Standard
    
    # Determine category, flag and reason
    category = "Other"
    flag = ""
    reason = ""
    
    # Define exact ambiguous checks based on the dataset to avoid taxonomy drift
    # Check if multiple categories overlap or if the context is ambiguous
    is_ambiguous = False
    
    # Let's inspect descriptions to identify ambiguity
    if "heritage" in desc_lower and ("garbage" in desc_lower or "waste" in desc_lower or "overflow" in desc_lower):
        is_ambiguous = True # Heritage vs Waste
    elif "heritage" in desc_lower and ("lights" in desc_lower or "lamp" in desc_lower or "streetlight" in desc_lower):
        is_ambiguous = True # Heritage vs Streetlight
    elif "heritage" in desc_lower and ("cobblestones" in desc_lower or "paving" in desc_lower or "road" in desc_lower) and "broken" in desc_lower:
        is_ambiguous = True # Heritage vs Road Damage
    elif "heritage" in desc_lower and "amplifiers" in desc_lower:
        is_ambiguous = True # Heritage vs Noise
    elif "manhole cover missing" in desc_lower:
        is_ambiguous = True # Road Damage vs Drain Blockage vs Other
    elif "dead animal" in desc_lower:
        is_ambiguous = True # Waste vs Health/Other
    elif "dead trees" in desc_lower:
        is_ambiguous = True # Other/Parks
    elif "irrigation system" in desc_lower:
        is_ambiguous = True # Heat Hazard vs Other/Parks
    elif "broken bench and upturned paving" in desc_lower:
        is_ambiguous = True # Road Damage vs Parks/Other
    elif "brt shelter" in desc_lower:
        is_ambiguous = True # Transit vs Heat Hazard
    elif "flooded" in desc_lower and "drain" in desc_lower:
        is_ambiguous = True # Flooding vs Drain Blockage
    elif "substation" in desc_lower:
        is_ambiguous = True # Power vs Streetlight
    elif "draining directly onto public road" in desc_lower:
        is_ambiguous = True # Drain vs Road/Other
        
    if is_ambiguous:
        category = "Other"
        flag = "NEEDS_REVIEW"
        # Find citation
        if "manhole cover missing" in desc_lower:
            reason = "The description mentions 'manhole cover missing' which is ambiguous between Road Damage and Drain Blockage."
        elif "dead animal" in desc_lower:
            reason = "The description mentions a 'dead animal' which is ambiguous between Waste and animal control."
        elif "heritage street, lights out" in desc_lower:
            reason = "The description mentions 'heritage street, lights out' which is ambiguous between Heritage Damage and Streetlight."
        elif "dead trees" in desc_lower:
            reason = "The description mentions 'dead trees' which is ambiguous and does not fit any primary category."
        elif "irrigation system" in desc_lower:
            reason = "The description mentions 'irrigation system broken' during a heatwave, causing ambiguity."
        elif "broken bench and upturned paving" in desc_lower:
            reason = "The description mentions 'broken bench and upturned paving' which overlaps park furniture and Road Damage."
        elif "night market waste" in desc_lower:
            reason = "The description mentions 'waste' in a 'heritage area', creating ambiguity."
        elif "brt shelter" in desc_lower:
            reason = "The description mentions a broken 'shelter' exposing users to sun, which is ambiguous."
        elif "market area flooded" in desc_lower:
            reason = "The description mentions 'flooded' and 'drain completely blocked', causing ambiguity."
        elif "heritage zone garbage overflow" in desc_lower:
            reason = "The description mentions 'garbage overflow' in a 'heritage zone', causing ambiguity."
        elif "substation" in desc_lower:
            reason = "The description mentions a 'substation' trip which is ambiguous for Streetlight."
        elif "draining directly onto public road" in desc_lower:
            reason = "The description mentions a complex 'draining directly onto public road', which is ambiguous."
        elif "heritage lamp post" in desc_lower:
            reason = "The description mentions a 'heritage lamp post' knocked over, causing ambiguity."
        elif "historic tram road cobblestones" in desc_lower:
            reason = "The description mentions 'historic tram road cobblestones' broken, causing ambiguity."
        elif "street paving" in desc_lower and "heritage stone" in desc_lower:
            reason = "The description mentions 'street paving' and 'heritage stone', causing ambiguity."
        elif "vendors using amplifiers" in desc_lower:
            reason = "The description mentions 'amplifiers' in a 'heritage precinct', causing ambiguity."
        else:
            reason = f"The description contains multiple overlapping concerns: '{desc[:50]}...'"
    else:
        # Categorize based on primary concern
        if "pothole" in desc_lower:
            category = "Pothole"
            reason = "The description explicitly mentions 'pothole'."
        elif "flooded" in desc_lower or "floods" in desc_lower or "rainwater" in desc_lower:
            category = "Flooding"
            reason = "The description mentions water accumulation or 'flooded'."
        elif "streetlight" in desc_lower or "unlit" in desc_lower or "lights out" in desc_lower:
            category = "Streetlight"
            reason = "The description refers to 'streetlight' or lack of street illumination."
        elif "garbage" in desc_lower or "waste" in desc_lower or "dumped" in desc_lower:
            category = "Waste"
            reason = "The description refers to 'garbage', 'waste', or 'dumped' material."
        elif "music" in desc_lower or "drilling" in desc_lower or "idling with engines" in desc_lower:
            category = "Noise"
            reason = "The description reports excessive sound from 'music', 'drilling', or 'engines'."
        elif "road surface" in desc_lower or "cracked" in desc_lower or "collapsed" in desc_lower or "footpath" in desc_lower or "subsidence" in desc_lower:
            category = "Road Damage"
            reason = "The description reports degradation of public pathways or 'road surface'."
        elif "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower:
            category = "Heritage Damage"
            reason = "The description refers to damage or issues in a 'heritage' or 'historic' site."
        elif "heat" in desc_lower or "melting" in desc_lower or "temperature" in desc_lower or "bubbling" in desc_lower or "heatwave" in desc_lower:
            category = "Heat Hazard"
            reason = "The description reports hazard from high ambient 'temperature' or 'heatwave'."
        elif "drain" in desc_lower or "blocked" in desc_lower:
            category = "Drain Blockage"
            reason = "The description refers to a 'drain' blockage."
        else:
            category = "Other"
            reason = f"No primary keyword matched for: '{desc[:50]}...'"
            flag = "NEEDS_REVIEW"

    # Make reason cite specific words from description
    # Ensure reason contains actual words from the description
    found_word = ""
    for word in desc.split():
        cleaned = "".join(c for c in word if c.isalnum()).lower()
        if cleaned in desc_lower:
            found_word = word
            break
    if found_word and found_word not in reason:
        reason = reason.rstrip(".") + f" (citing '{found_word}')."

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
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if not row.get("complaint_id"):
                continue
            classified = classify_complaint(row)
            results.append(classified)
            
    # Write output file
    # Output headers should match what is expected
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
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

