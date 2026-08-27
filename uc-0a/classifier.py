import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # Determine Priority based on strict severity keywords
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # Determine Category, Reason, and Flag
    category = "Other"
    reason = "The issue could not be confidently categorized."
    flag = ""
    
    # Simple heuristic to simulate classification based on keywords
    if "pothole" in desc_lower:
        category = "Pothole"
        reason = "The description explicitly mentions a 'pothole'."
    elif "drain" in desc_lower:
        category = "Drain Blockage"
        reason = "The description mentions that a 'drain blocked'."
    elif "flood" in desc_lower or "water" in desc_lower:
        category = "Flooding"
        reason = "The description cites being 'flooded' or 'water'."
    elif "streetlight" in desc_lower or "lights out" in desc_lower:
        category = "Streetlight"
        reason = "The description notes a 'streetlight' issue or 'lights out'."
    elif "garbage" in desc_lower or "waste" in desc_lower or "animal" in desc_lower:
        category = "Waste"
        reason = "The description refers to 'garbage', 'waste', or a 'dead animal'."
    elif "music" in desc_lower or "noise" in desc_lower:
        category = "Noise"
        reason = "The description explicitly mentions 'music' or noise."
    elif "road surface" in desc_lower or "footpath" in desc_lower or "manhole" in desc_lower:
        category = "Road Damage"
        reason = "The description mentions a damaged 'road surface', 'footpath', or 'manhole'."
    else:
        # Genuine ambiguity flag as required by schema
        flag = "NEEDS_REVIEW"
        reason = "The complaint is ambiguous and requires manual review."
        
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
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Error parsing row: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
