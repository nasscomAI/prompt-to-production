"""
UC-0A — Complaint Classifier
Rule-based implementation guided by agents.md and skills.md.
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Simple keyword-to-category mapping for rule-based classification
CATEGORY_HINTS = {
    "Pothole": ["pothole", "crater", "sinkhole"],
    "Flooding": ["flood", "water", "rain", "underpass", "submerged"],
    "Streetlight": ["light", "dark", "street lamp", "flicker", "sparking"],
    "Waste": ["garbage", "trash", "waste", "bins", "dumped", "smell"],
    "Noise": ["noise", "loud", "music", "sound", "volume"],
    "Road Damage": ["cracked", "sinking", "surface", "pavement"],
    "Heritage Damage": ["heritage", "old city", "historic"],
    "Drain Blockage": ["drain", "sewage", "manhole", "blockage"],
    "Heat Hazard": ["heat", "hot", "sun", "exhaustion"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Determine Category
    category = "Other"
    matched_word = ""
    
    for cat, hints in CATEGORY_HINTS.items():
        for hint in hints:
            if hint in description:
                category = cat
                matched_word = hint
                break
        if category != "Other":
            break
            
    # 2. Determine Priority
    priority = "Standard"
    urgent_reason = ""
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            urgent_reason = kw
            break
            
    # 3. Handle Ambiguity/Flag
    flag = ""
    if category == "Other" or not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 4. Construct Reason (Evidence-based)
    if category != "Other" and matched_word:
        reason = f"Classified as {category} because the description mentions '{matched_word}'."
    elif not description:
        reason = "Empty description provided."
    else:
        reason = "Could not confidently match description to a specific category."
        
    if priority == "Urgent" and urgent_reason:
        reason += f" Priority set to Urgent due to safety keyword '{urgent_reason}'."
    elif priority == "Standard" and not flag:
        reason += " No urgent safety keywords detected."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                classified_row = classify_complaint(row)
                results.append(classified_row)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
