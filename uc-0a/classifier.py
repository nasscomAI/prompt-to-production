import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    # Priority logic based on keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_keywords = [kw for kw in severity_keywords if kw in desc]
    
    if found_keywords:
        priority = "Urgent"
        kw = found_keywords[0]
        reason = f"Found severe keyword '{kw}' in description."
    else:
        priority = "Standard"
        reason = "No severe keywords found."

    # Category logic based on exact strings allowed
    allowed_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    
    category = "Other"
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
    elif "streetlight" in desc or "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "animal" in desc or "dump" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
    elif "road" in desc and ("crack" in desc or "sink" in desc or "damage" in desc):
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc:
        category = "Drain Blockage"
    
    flag = ""
    # Flag needs review if ambiguous (multiple category words)
    if ("pothole" in desc and "water" in desc) or ("drain" in desc and "water" in desc):
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
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                pass
                
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
