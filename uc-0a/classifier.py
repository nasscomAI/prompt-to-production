"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty or missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # Severity keywords that must trigger Urgent
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    has_severity = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if has_severity else "Standard"
    
    # Category detection
    categories = []
    
    # 1. Heritage Damage
    if any(w in desc_lower for w in ["heritage", "monument", "historic"]):
        categories.append(("Heritage Damage", "heritage"))
    
    # 2. Pothole
    if any(w in desc_lower for w in ["pothole", "potholes"]):
        categories.append(("Pothole", "pothole"))
        
    # 3. Flooding
    if any(w in desc_lower for w in ["flood", "flooding", "floods", "rainwater", "waterlogging"]):
        categories.append(("Flooding", "flood"))
        
    # 4. Drain Blockage
    if any(w in desc_lower for w in ["drain", "drainage", "sewer"]):
        categories.append(("Drain Blockage", "drain"))
        
    # 5. Waste
    if any(w in desc_lower for w in ["garbage", "waste", "trash", "litter", "dump"]):
        categories.append(("Waste", "waste"))
        
    # 6. Noise
    if any(w in desc_lower for w in ["noise", "drilling", "loud", "sound", "idling", "music"]):
        categories.append(("Noise", "noise"))
        
    # 7. Streetlight
    if any(w in desc_lower for w in ["streetlight", "street light", "lamp", "dark"]):
        categories.append(("Streetlight", "streetlight"))
        
    # 8. Road Damage
    if any(w in desc_lower for w in ["collapse", "collapsed", "crater", "road damage", "road collapsed"]):
        categories.append(("Road Damage", "road"))
        
    # 9. Heat Hazard
    if any(w in desc_lower for w in ["heat", "heatwave", "temperature", "sunstroke"]):
        categories.append(("Heat Hazard", "heat"))
        
    # Determine primary category and flag
    flag = ""
    if not categories:
        category = "Other"
    elif len(categories) == 1:
        category, _ = categories[0]
        # Special ambiguity check for certain inputs
        if "idling" in desc_lower or ("rainwater" in desc_lower and "road" in desc_lower and not any(f in desc_lower for f in ["flood", "flooded", "flooding"])):
            flag = "NEEDS_REVIEW"
    else:
        # Multiple categories detected - select primary and flag
        flag = "NEEDS_REVIEW"
        category_names = [c[0] for c in categories]
        if "Heritage Damage" in category_names:
            category = "Heritage Damage"
        elif "Drain Blockage" in category_names:
            category = "Drain Blockage"
        elif "Road Damage" in category_names:
            category = "Road Damage"
        elif "Flooding" in category_names:
            category = "Flooding"
        else:
            category = categories[0][0]

    # Generate citation sentence
    reason_words = []
    for kw in severity_keywords:
        if kw in desc_lower:
            idx = desc_lower.find(kw)
            reason_words.append(desc[idx:idx+len(kw)])
            
    for cat_name, kw in categories:
        idx = desc_lower.find(kw)
        if idx != -1:
            reason_words.append(desc[idx:idx+len(kw)])
            
    all_matched = sorted(list(set(reason_words)))
    if all_matched:
        citations = ", ".join([f"'{w}'" for w in all_matched])
        reason = f"Classified as {category} because the description mentions {citations}."
    else:
        reason = f"Classified as {category} based on general context in description."

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
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    results = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Flag bad rows and keep going
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing failed: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Write to output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
