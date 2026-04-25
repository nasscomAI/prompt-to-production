"""
UC-0A — Complaint Classifier
Implemented based on agents.md and skills.md requirements.
"""
import argparse
import csv
import os

# Configuration from agents.md and README.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance', 
    'fire', 'hazard', 'fell', 'collapse'
]

CATEGORY_MAP = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "flooding", "water"],
    "Streetlight": ["streetlight", "light", "lamp", "dark"],
    "Waste": ["garbage", "waste", "trash", "dump", "bin", "animal"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road", "crack", "pavement", "footpath", "sinking"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "hot", "sun"],
    "Drain Blockage": ["drain", "sewage", "clog", "manhole"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # Error handling for empty descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description for classification.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    
    # 1. Determine Priority (Safety Trigger)
    priority = "Standard"
    triggered_safety_word = None
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            priority = "Urgent"
            triggered_safety_word = word
            break
    
    # 2. Determine Category (Mapping & Ambiguity Handling)
    matched_categories = []
    matched_words = []
    
    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                matched_words.append(kw)
                break # Move to next category if one keyword matches
    
    # Remove duplicates from multiple keywords in same category
    matched_categories = list(set(matched_categories))
    
    category = "Other"
    flag = ""
    reason_cite = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason_cite = f"quotes '{matched_words[0]}'"
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = f"spans multiple categories: {', '.join(matched_categories)}"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "does not fit specific categories"
        
    # 3. Construct Reason (Single sentence citing specific words)
    if priority == "Urgent" and triggered_safety_word:
        reason = f"Classified as {category} with Urgent priority because description {reason_cite} and mentions safety hazard '{triggered_safety_word}'."
    else:
        reason = f"Classified as {category} because the description {reason_cite}."

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
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if 'description' not in reader.fieldnames:
            raise ValueError(f"CSV missing 'description' column. Found: {reader.fieldnames}")
            
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Robustness: flag nulls/errors and produce partial output
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"System error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    if not results:
        print("No rows to process.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
    except Exception as e:
        print(f"Fatal error: {e}")
