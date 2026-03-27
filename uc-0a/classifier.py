"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    matched_categories = []
    for cat in CATEGORIES:
        if cat.lower() in desc:
            matched_categories.append(cat)
        elif cat == "Road Damage" and "road" in desc and ("broken" in desc or "buckled" in desc or "subsided" in desc):
            matched_categories.append(cat)
        elif cat == "Heritage Damage" and "heritage" in desc:
            matched_categories.append(cat)
        elif cat == "Streetlight" and ("lamp" in desc or "darkness" in desc or "light" in desc):
            matched_categories.append(cat)
        elif cat == "Pothole" and "pothole" in desc:
            matched_categories.append(cat)
        elif cat == "Noise" and ("amplifier" in desc or "band" in desc or "noise" in desc):
            matched_categories.append(cat)
        elif cat == "Waste" and "waste" in desc:
            matched_categories.append(cat)
            
    # Deduplicate
    matched_categories = list(set(matched_categories))
    
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    if found_severity:
        priority = "Urgent"
        reason_word = found_severity[0]
    else:
        priority = "Standard"
        words = desc.split()
        reason_word = words[0] if words else "description"
        
    reason = f"The description mentions the word '{reason_word}'."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


import os

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        # Ensure output directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", default="../data/city-test-files/test_pune.csv", help="Path to test_[city].csv")
    parser.add_argument("--output", default="../results_data/results_pune.csv", help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
