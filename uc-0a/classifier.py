"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    category = "Other"
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc or "smell" in desc or "animal" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
    elif "crack" in desc or "surface" in desc or "broken" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    found_keywords = [kw for kw in severity_keywords if kw in desc]
    if found_keywords:
        priority = "Urgent"
        reason = f"Contains severity keyword(s): {', '.join(found_keywords)}."
    else:
        priority = "Standard"
        reason = "Standard priority based on description."
        
    flag = ""
    # simple ambiguity check
    cat_keywords = {"pothole": "Pothole", "flood": "Flooding", "light": "Streetlight", "waste": "Waste"}
    found_cats = [v for k, v in cat_keywords.items() if k in desc]
    if len(found_cats) > 1:
        flag = "NEEDS_REVIEW"
        reason += f" Ambiguous categories found: {', '.join(found_cats)}."
        
    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                out_row = {**row, **res}
                results.append(out_row)
            except Exception as e:
                print(f"Failed to process row {row}: {e}")
                
    if results:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = list(results[0].keys())
            for k in ["category", "priority", "reason", "flag"]:
                if k not in fieldnames:
                    fieldnames.append(k)
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
