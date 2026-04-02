"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    # Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Low"
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            break
    if priority == "Low":
        priority = "Standard"
            
    # Categories
    category = "Other"
    reasons_kw = ""
    if "pothole" in desc:
        category = "Pothole"
        reasons_kw = "pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
        reasons_kw = "flood"
    elif " streetlight" in desc or "lights out" in desc or "dark" in desc:
        category = "Streetlight"
        reasons_kw = "streetlight or dark"
    elif "garbage" in desc or "waste" in desc:
        category = "Waste"
        reasons_kw = "garbage or waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reasons_kw = "music or noise"
    elif "crack" in desc or "footpath" in desc:
        category = "Road Damage"
        reasons_kw = "crack or footpath"
    elif "heritage" in desc:
        category = "Heritage Damage"
        reasons_kw = "heritage"
    elif "drain" in desc:
        category = "Drain Blockage"
        reasons_kw = "drain"
    elif "dead animal" in desc:
        category = "Other"
        reasons_kw = "dead animal"
        
    reason = f"Classified dynamically based on matching keywords like {reasons_kw}." if reasons_kw else "No matching category keyword found."
    
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                out_kw = classify_complaint(row)
                results.append(out_kw)
            except Exception as e:
                print(f"Skipping row due to error: {e}")
                
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
