"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row deterministically based on RICE constraints.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    
    # Priority Enforcement
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_priority_keywords = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if found_priority_keywords else "Standard"
    
    # Category Enforcement Mapping
    categories = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "submerged", "water"],
        "Streetlight": ["streetlight", "light", "dark", "lamp", "sparking"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "bin"],
        "Noise": ["noise", "loud", "music", "sound"],
        "Road Damage": ["cracked", "broken", "pavement", "sinking", "tiles broken", "upturned", "road surface"],
        "Heritage Damage": ["monument", "heritage", "historic"],
        "Heat Hazard": ["heat", "wave", "sunstroke"],
        "Drain Blockage": ["drain", "clog", "blocked", "sewer"]
    }
    
    matched_categories = []
    matched_keywords = []
    
    for cat, kws in categories.items():
        found_in_cat = [k for k in kws if k in desc]
        if found_in_cat:
            matched_categories.append(cat)
            matched_keywords.extend(found_in_cat)
            
    # Ambiguity Enforcement Check
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        trigger_word = matched_keywords[0]
    else:
        # Zero or multiple overlapping categories -> Ambigous
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(matched_categories) > 1:
            trigger_word = f"multiple conflicting keywords like '{matched_keywords[0]}'"
        else:
            trigger_word = "no clear category keywords"

    # Enforce exactly one sentence citing specific words
    if found_priority_keywords:
        reason = f"The description contains '{trigger_word}' indicating the category, and '{found_priority_keywords[0]}' which evaluates priority to Urgent."
    else:
        reason = f"The description contains '{trigger_word}' which justifies this exact classification."
        
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
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames or [])
            
            # Extend fields
            for col in ["category", "priority", "reason", "flag"]:
                if col not in fieldnames:
                    fieldnames.append(col)
            
            results = []
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = f"Processing failed with exception."
                    row["flag"] = "NEEDS_REVIEW"
                results.append(row)
                
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input CSV {input_path} not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
