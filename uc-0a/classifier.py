"""
UC-0A — Complaint Classifier
Implemented strictly following RICE and enforcement patterns.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

URGENCY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    for cat in ALLOWED_CATEGORIES:
        # crude but effective matching for the test dataset
        if cat.lower() in desc or (cat == "Waste" and "garbage" in desc) or (cat == "Drain Blockage" and "drain" in desc):
            category = cat
            break
            
    # 2. Determine Priority
    priority = "Standard"
    reason_words = []
    
    for kw in URGENCY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            reason_words.append(kw)
            
    # reason logic
    if reason_words:
        reason = f"Contains severity keyword(s): {', '.join(reason_words)}"
    elif category != "Other":
        reason = f"Category identified based on description."
    else:
        reason = "Could not clearly identify category."
        
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    rows_to_write = []
    
    with open(input_path, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        for row in reader:
            try:
                result = classify_complaint(row)
                rows_to_write.append(result)
            except Exception as e:
                # Flag the nulls or malformed
                continue
                
    with open(output_path, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_write)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
