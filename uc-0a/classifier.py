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
    desc = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()
    
    if not desc or not complaint_id:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description or complaint ID.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # Priority Rule: Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    matched_priorities = []
    for kw in severity_keywords:
        if kw in desc_lower:
            is_urgent = True
            matched_priorities.append(kw)
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # Category detection rules
    category = "Other"
    flag = ""
    reason_cite = ""
    
    # 1. Drain Blockage
    if "drain" in desc_lower or "manhole" in desc_lower or "choked" in desc_lower:
        category = "Drain Blockage"
        for w in ["storm water drain", "stormwater drain", "main drain", "drain", "manhole", "choked"]:
            if w in desc_lower:
                reason_cite = w
                break
        if not reason_cite:
            reason_cite = "drain/manhole"
            
    # 2. Pothole
    elif "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
        for w in ["pothole", "potholes", "crater"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    # 3. Flooding
    elif "flood" in desc_lower or "water logging" in desc_lower or "waterlogging" in desc_lower or "submerged" in desc_lower or "rainwater" in desc_lower:
        category = "Flooding"
        for w in ["water logging", "waterlogging", "flooded", "flooding", "submerged", "floods", "rainwater"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    # 4. Streetlight
    elif "streetlight" in desc_lower or "street light" in desc_lower or "streetlights" in desc_lower or "unlit" in desc_lower or "darkness" in desc_lower or "flickering" in desc_lower or "sparking" in desc_lower or "street pole" in desc_lower:
        category = "Streetlight"
        for w in ["streetlight", "streetlights", "unlit", "darkness", "flickering", "sparking", "street pole", "lights out"]:
            if w in desc_lower:
                reason_cite = w
                break
        if not reason_cite:
            reason_cite = "light/pole"
            
    # 5. Waste
    elif "waste" in desc_lower or "garbage" in desc_lower or "bins" in desc_lower or "dumped" in desc_lower or "litter" in desc_lower or "trash" in desc_lower or "refuse" in desc_lower or "debris" in desc_lower:
        category = "Waste"
        for w in ["waste", "garbage", "bins", "dumped", "litter", "trash", "debris"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    # 6. Noise
    elif "music" in desc_lower or "noise" in desc_lower or "loud" in desc_lower or "horn" in desc_lower or "honking" in desc_lower or "sound" in desc_lower or "amplifier" in desc_lower or "drilling" in desc_lower or "audible" in desc_lower:
        category = "Noise"
        for w in ["music", "noise", "loud", "horn", "honking", "sound", "amplifier", "amplifiers", "drilling", "audible"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    # 7. Heritage Damage
    elif "heritage" in desc_lower or "historic" in desc_lower or "museum" in desc_lower or "statue" in desc_lower or "monument" in desc_lower or "ancient" in desc_lower:
        category = "Heritage Damage"
        for w in ["heritage", "historic", "museum", "statue", "monument", "ancient"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    # 8. Heat Hazard
    elif "melting" in desc_lower or "heatwave" in desc_lower or "temperature" in desc_lower or "heat" in desc_lower or "hot" in desc_lower or "sun" in desc_lower or "bubbling" in desc_lower:
        category = "Heat Hazard"
        for w in ["melting", "heatwave", "temperature", "temperatures", "heat", "hot", "sun", "bubbling"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    # 9. Road Damage
    elif "road" in desc_lower or "paving" in desc_lower or "cobblestones" in desc_lower or "divider" in desc_lower or "surface" in desc_lower or "bridge" in desc_lower or "underpass" in desc_lower or "sidewalk" in desc_lower or "footpath" in desc_lower or "subside" in desc_lower or "collapse" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower or "buckled" in desc_lower or "tarmac" in desc_lower:
        category = "Road Damage"
        for w in ["paving", "cobblestones", "divider", "dividers", "surface", "bridge", "underpass", "sidewalk", "footpath", "subside", "subsidence", "collapse", "collapsed", "cracked", "sinking", "buckled", "tarmac", "road"]:
            if w in desc_lower:
                reason_cite = w
                break
                
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "unrecognized complaint description"

    # Post-check for ambiguous or multi-category conflictual descriptions:
    has_heritage = any(h in desc_lower for h in ["heritage", "historic", "museum", "statue", "monument", "ancient"])
    has_waste = any(ws in desc_lower for ws in ["waste", "garbage", "bins", "dumped", "litter", "trash", "debris"])
    has_noise = any(n in desc_lower for n in ["music", "noise", "loud", "horn", "honking", "sound", "amplifier", "amplifiers", "drilling", "audible"])
    
    if has_heritage and (has_waste or has_noise):
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = f"ambiguous combination of heritage and {'waste' if has_waste else 'noise'}"
    
    if "stray bull" in desc_lower or "animal" in desc_lower:
        if "stray bull" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason_cite = "stray bull"
        elif "dead animal" in desc_lower:
            category = "Waste"
            reason_cite = "dead animal"
            flag = ""

    if flag == "NEEDS_REVIEW":
        reason = f"Classified as Other and flagged for review because the description cites '{reason_cite}' which is ambiguous or not covered by standard categories."
    else:
        if is_urgent:
            reason = f"Classified as {category} with Urgent priority due to severity keyword '{matched_priorities[0]}' and reference to '{reason_cite}'."
        else:
            reason = f"Classified as {category} with Standard priority based on the mention of '{reason_cite}' in the description."

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
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not any(row.values()):
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file {input_path}: {e}")
        return

    # Write output file
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
