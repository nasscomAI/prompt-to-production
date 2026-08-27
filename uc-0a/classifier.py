"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole", "crater", "hole", "cave-in", "caved"],
    "Flooding": ["flood", "water", "overflow", "submerged", "drainage issue"],
    "Streetlight": ["streetlight", "light", "dark", "bulb", "lamp"],
    "Waste": ["waste", "garbage", "trash", "dump", "rubbish"],
    "Noise": ["noise", "loud", "sound", "music", "construction"],
    "Road Damage": ["road", "damage", "crack", "pavement", "broken"],
    "Heritage Damage": ["heritage", "monument", "statue", "historic", "plaque"],
    "Heat Hazard": ["heat", "sun", "temperature", "wave"],
    "Drain Blockage": ["drain", "blockage", "clog", "sewer"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    priority = "Standard"
    matched_urgent_words = []
    for word in URGENT_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', desc_lower):
            priority = "Urgent"
            matched_urgent_words.append(word)
            
    category = "Other"
    matched_cat_words = []
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                category = cat
                matched_cat_words.append(kw)
                break
        if category != "Other":
            break

    flag = "NEEDS_REVIEW" if category == "Other" else ""
        
    if matched_urgent_words and matched_cat_words:
        reason = f"Classified as {category} with {priority} priority because the description mentions '{matched_cat_words[0]}' and severity keyword '{matched_urgent_words[0]}'."
    elif matched_urgent_words:
        reason = f"Classified as {category} with {priority} priority because the description mentions severity keyword '{matched_urgent_words[0]}'."
    elif matched_cat_words:
        reason = f"Classified as {category} with {priority} priority because the description mentions '{matched_cat_words[0]}'."
    else:
        reason = "Classified as Other because no specific category keywords were found in the description."

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
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            rows_to_write = []
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    rows_to_write.append(classification)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    rows_to_write.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except Exception as e:
        print(f"Failed to process file {input_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
