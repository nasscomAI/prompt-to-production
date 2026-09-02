"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority classification
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    reason_words = []
    
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            reason_words.append(kw)
            
    if not reason_words:
        # just pick a descriptive word
        words = [w for w in desc.split() if len(w) > 4]
        if words:
            reason_words.append(words[0])
            
    reason = f"Based on description mentioning '{reason_words[0]}'" if reason_words else "Based on general description"
    
    # Category classification
    category = "Other"
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "animal" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "crack" in desc or "sinking" in desc or "manhole" in desc or "footpath" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "drain" in desc or "block" in desc:
        category = "Drain Blockage"
        
    # Edge case from data:
    if "drain blocked" in desc:
        category = "Drain Blockage"
        
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
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
