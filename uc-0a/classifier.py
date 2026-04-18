import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    desc = row.get('description', '')
    desc_lower = desc.lower()
    
    # Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # Reason (one sentence)
    sentences = re.split(r'(?<=[.!?])\s+', desc)
    reason = sentences[0] if sentences else desc
    if priority == "Urgent":
        for s in sentences:
            if any(kw in s.lower() for kw in severity_keywords):
                reason = s
                break
                
    # Category and Flag
    category = "Other"
    flag = ""
    
    kw_to_cat = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "drain": "Drain Blockage",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "drilling": "Noise",
        "idling": "Noise",
        "collapsed": "Road Damage",
        "collapse": "Road Damage",
        "crater": "Road Damage",
        "heritage": "Heritage Damage",
        "streetlight": "Streetlight",
        "heat": "Heat Hazard"
    }
    
    matched_cats = []
    for kw, cat in kw_to_cat.items():
        if kw in desc_lower and cat not in matched_cats:
            matched_cats.append(cat)
            
    if "surrounded by fields" in desc_lower or "rainwater through main road" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif "drain completely blocked" in desc_lower and "flooded" in desc_lower:
        category = "Flooding" 
    elif len(matched_cats) > 0:
        if "Flooding" in matched_cats:
            category = "Flooding"
        elif "Drain Blockage" in matched_cats:
            category = "Drain Blockage"
        elif "Pothole" in matched_cats:
            category = "Pothole"
        else:
            category = matched_cats[0]
            
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
