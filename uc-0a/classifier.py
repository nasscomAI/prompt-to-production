"""
UC-0A — Complaint Classifier
Implemented utilizing guidelines from agents.md and skills.md.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with updated category, priority, reason, and flag fields.
    """
    description = str(row.get("description", "")).lower()
    
    # 1. Map keywords to categories
    categories_map = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlog", "submerge", "water level"],
        "Streetlight": ["streetlight", "street light", "light out", "dark"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "debris"],
        "Noise": ["noise", "loud", "music", "sound"],
        "Road Damage": ["road damage", "crack", "broken road", "uneven"],
        "Heritage Damage": ["heritage", "monument", "statue", "historical"],
        "Heat Hazard": ["heat", "sun", "temperature"],
        "Drain Blockage": ["drain", "clog", "block", "sewer", "overflow"],
    }
    
    matched_categories = []
    for cat, keywords in categories_map.items():
        if any(kw in description for kw in keywords):
            matched_categories.append(cat)
            
    # Strict matching - Needs review if ambiguous
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Priority severity extraction
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    priority = "Standard"
    matched_severity = None
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            matched_severity = kw
            break
            
    # 3. Extract exactly one sentence for reason sighting specific words
    sentences = re.split(r'(?<=[.!?])\s+', row.get("description", ""))
    reason_sentence = "No description found."
    if sentences:
        reason_sentence = sentences[0]
        for s in sentences:
            s_lower = s.lower()
            if matched_severity and matched_severity in s_lower:
                reason_sentence = s.strip()
                break
            if not matched_severity and any(kw in s_lower for kws in categories_map.values() for kw in kws):
                reason_sentence = s.strip()
                break
                
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = f"Mentioned: {reason_sentence}"
    result["flag"] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row interactively utilizing classify_complaint, 
    and output results CSV. Error resilient.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Input CSV is empty or missing headers.")
                return
            
            # Add required columns if not present
            for new_col in ["category", "priority", "reason", "flag"]:
                if new_col not in fieldnames:
                    fieldnames.append(new_col)
                    
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as e:
            print(f"Failed to parse row: {row.get('complaint_id', 'unknown')}. Error {e}. Row skipped.")
            
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Classified batch written to {args.output}")
