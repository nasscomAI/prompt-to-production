"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "")
    desc_lower = desc.lower()
    
    # Priority & Reason mapping based on severity keywords
    priority = "Standard"
    reason = "Classified based on general description."
    flag = ""
    
    for word in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', desc_lower):
            priority = "Urgent"
            reason = f"Marked urgent due to severity keyword '{word}' in description."
            break
            
    # Simple keyword mapping for category
    category = "Other"
    cat_reasons = {
        "pothole": "Pothole",
        "flood": "Flooding", "waterlogging": "Flooding",
        "light": "Streetlight", "lamp": "Streetlight",
        "garbage": "Waste", "waste": "Waste", "trash": "Waste",
        "speaker": "Noise", "loud": "Noise", "noise": "Noise",
        "road damage": "Road Damage",
        "monument": "Heritage Damage", "heritage": "Heritage Damage",
        "heat": "Heat Hazard", "temperature": "Heat Hazard",
        "drain": "Drain Blockage", "sewage": "Drain Blockage"
    }
    
    for kw, cat in cat_reasons.items():
        if kw in desc_lower:
            category = cat
            if priority == "Standard":
                reason = f"Classified as {cat} due to keyword '{kw}'."
            break
            
    if "issue" in desc_lower and category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Genuinely ambiguous description lacking specific category keywords."

    return {
        "complaint_id": row.get("complaint_id", row.get("id", "")),
        "description": desc,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                results.append(classify_complaint(row))
    except Exception as e:
        print(f"Error reading input: {e}")
        return
        
    if results:
        fieldnames = ["complaint_id", "description", "category", "priority", "reason", "flag"]
        try:
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing output: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
