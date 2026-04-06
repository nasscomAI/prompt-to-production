"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    category = "Other"
    priority = "Low"
    reason = "The description contains ambiguous details."
    flag = ""
    
    urgent_kws = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(kw in desc for kw in urgent_kws):
        priority = "Urgent"
    else:
        priority = "Standard"
        
    if "pothole" in desc:
        category = "Pothole"
        reason = "Description mentions 'pothole'."
    elif "flood" in desc:
        category = "Flooding"
        reason = "Description mentions 'flood'."
    elif "drain" in desc:
        category = "Drain Blockage"
        reason = "Description mentions 'drain'."
    elif "streetlight" in desc or "lights out" in desc:
        category = "Streetlight"
        reason = "Description mentions 'streetlight' or 'lights'."
    elif "garbage" in desc or "waste" in desc:
        category = "Waste"
        reason = "Description mentions 'garbage' or 'waste'."
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason = "Description mentions 'music'."
    elif "crack" in desc or "surface" in desc or "tiles broken" in desc or "manhole" in desc:
        category = "Road Damage"
        reason = "Description mentions road 'crack', 'surface', or 'tiles broken'."
    elif "heritage" in desc:
        category = "Heritage Damage" 
        reason = "Description mentions 'heritage'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if "animal" in desc:
            reason = "Description mentions 'animal', causing category ambiguity."
        else:
            reason = "Description is missing clear category keywords."
            
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    for row in rows:
        try:
            res = classify_complaint(row)
            row.update(res)
        except Exception:
            row.update({"category": "Other", "priority": "Low", "reason": "Error", "flag": "NEEDS_REVIEW"})
            
    if not rows:
        return
        
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
