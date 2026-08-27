"""
UC-0A — Complaint Classifier
(Rule-Based Fallback to avoid OpenAI API)
"""
import argparse
import csv
import sys
import re

# Categories from Schema
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords for Priority
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Rule-based complaint classification enforcing agents.md & skills.md logic.
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine priority based strictly on severity keywords
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            break
            
    # 2. Determine category based on keyword matching
    category = "Other"
    
    if any(word in desc for word in ["pothole", "crater"]):
        category = "Pothole"
    elif any(word in desc for word in ["flood", "waterlogging", "rain"]):
        category = "Flooding"
    elif any(word in desc for word in ["light", "dark", "streetlight"]):
        category = "Streetlight"
    elif any(word in desc for word in ["garbage", "waste", "trash", "dump"]):
        category = "Waste"
    elif any(word in desc for word in ["noise", "loud", "music", "bark"]):
        category = "Noise"
    elif any(word in desc for word in ["road", "broken surface", "asphalt"]):
        category = "Road Damage"
    elif any(word in desc for word in ["heritage", "monument", "statue"]):
        category = "Heritage Damage"
    elif any(word in desc for word in ["heat", "sun", "temperature"]):
        category = "Heat Hazard"
    elif any(word in desc for word in ["drain", "clog", "sewer"]):
        category = "Drain Blockage"
        
    # 3. Determine flag for ambiguous cases
    flag = ""
    # Check if multiple category indicators are present (ambiguous)
    # Simple heuristic: if we matched Other, or if the text is super short with no clear keywords
    if category == "Other" and len(desc) < 20:
        flag = "NEEDS_REVIEW"
        
    return {
        "category": category,
        "priority": priority,
        "reason": f"Classified based on keywords mapped to {category}.",
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return
        
    for i, row in enumerate(rows):
        # Apply the rule-based logic to each row
        class_res = classify_complaint(row)
        
        output_row = {**row}
        output_row["category"] = class_res.get("category", "Other")
        output_row["priority"] = class_res.get("priority", "Standard")
        output_row["reason"] = class_res.get("reason", "")
        output_row["flag"] = class_res.get("flag", "")
        
        results.append(output_row)
        
    if results:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = list(results[0].keys())
            # Ensure standard fields appear at end if not already present
            for req in ["category", "priority", "reason", "flag"]:
                if req not in fieldnames:
                    fieldnames.append(req)
                    
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Rule-based Results written to {args.output}")
