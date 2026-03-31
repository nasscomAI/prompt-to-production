"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with category, priority, reason, flag.
    """
    import re
    # Combine all values in the row to safely search for keywords
    text = str(row).lower()
    
    URGENT_KEYWORDS = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    # 1. Determine Priority
    priority = "Standard"
    found_urgent = []
    for w in URGENT_KEYWORDS:
        if w in text:
            found_urgent.append(w)
            
    if found_urgent:
        priority = "Urgent"

    # 2. Category Maps based on README.md allowed values
    kw_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlog"],
        "Streetlight": ["streetlight", "street light", "dark", "no light", "light"],
        "Waste": ["garbage", "trash", "waste", "dump", "dead animal"],
        "Noise": ["loud", "noise", "music"],
        "Road Damage": ["crack", "road damage", "broken road", " road surface"],
        "Heritage Damage": ["monument", "heritage", "statue"],
        "Heat Hazard": ["heat", "sun", "hot"],
        "Drain Blockage": ["drain", "clog", "sewer", "block", "blockage"]
    }
    
    matches = {}
    for cat, kws in kw_map.items():
        for kw in kws:
            if kw in text:
                if cat not in matches:
                    matches[cat] = kw
                    
    category = "Other"
    flag = ""
    reason = ""
    
    if len(matches) == 1:
        category = list(matches.keys())[0]
        keyword = matches[category]
        reason = f"Classified based on '{keyword}'."
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous due to conflicting keywords: {', '.join(matches.values())}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No matching keyword found in the text."
        
    if priority == "Urgent":
        # Modify reason to explicitly mention urgent keyword
        reason = reason[:-1] + f", marked urgent due to '{found_urgent[0]}'."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely handles bad rows and ensures headers are present.
    """
    import csv
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            
            # Ensure our newly generated columns exist
            for f in ["category", "priority", "reason", "flag"]:
                if f not in fieldnames:
                    fieldnames.append(f)
                    
            results = []
            for row in reader:
                try:
                    # Skip completely empty rows
                    if not any(row.values()):
                        continue
                        
                    classification = classify_complaint(row)
                    row.update(classification)
                except Exception as e:
                    print(f"Warning: Failed to process row. Error: {e}")
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = "Failed to classify due to error."
                    row["flag"] = "NEEDS_REVIEW"
                results.append(row)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
