"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Categories from agents.md constraints
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

# Keywords mapping
KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "flooded", "waterlogging", "knee-deep"],
    "Streetlight": ["streetlight", "lamp post", "darkness", "lights out"],
    "Waste": ["waste", "garbage", "trash", "overflowing", "dumped"],
    "Noise": ["noise", "music", "loud", "amplifiers", "drilling"],
    "Road Damage": ["road surface", "road subsided", "road collapsed", "tarmac surface", "footpath", "paving"],
    "Heritage Damage": ["heritage", "monument", "ancient step well", "tagore museum", "bow barracks", "marble palace"],
    "Heat Hazard": ["44°c", "45°c", "52°c", "heatwave", "metal bus shelter", "unbearable", "burns"],
    "Drain Blockage": ["drain blocked", "drain completely blocked", "drain", "mosquito breeding"]
}

# Priorities from agents.md logic
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse", "hospitalised", "stranded", "risk"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    
    # 1. Determine Category
    matched_categories = []
    reason_words = []
    
    for category, kws in KEYWORDS.items():
        for kw in kws:
            if kw in desc:
                if category not in matched_categories:
                    matched_categories.append(category)
                    reason_words.append(kw)
                break
                
    if len(matched_categories) == 1:
        final_category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        # Check if one is a more specific subset (e.g., Road Damage vs Pothole, prioritize Pothole)
        if "Pothole" in matched_categories and "Road Damage" in matched_categories:
            final_category = "Pothole"
            flag = ""
        else:
            final_category = "Other"
            flag = "NEEDS_REVIEW"
    else:
        final_category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            reason_words.append(kw)
            break
            
    # 3. Create Reason
    if not reason_words:
        reason = "Description ambiguous."
    else:
        words_str = ", ".join([f"'{w}'" for w in set(reason_words)])
        reason = f"The description contains specific keywords like {words_str} justifying this classification."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": final_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
         print(f"Error writing to output file '{output_path}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
