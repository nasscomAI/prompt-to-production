import argparse
import csv
import re
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the defined taxonomy and priority rules.
    """
    description = row.get("description", "")
    if description is None:
        description = ""
    
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # Category detection mapping
    category_map = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlogging", "water on road", "submerged"],
        "Streetlight": ["light", "streetlight", "lamp", "dark"],
        "Waste": ["garbage", "trash", "waste", "dump", "debris"],
        "Noise": ["noise", "loud", "sound", "music", "honking"],
        "Road Damage": ["road damage", "crack", "broken road", "uneven"],
        "Heritage Damage": ["heritage", "statue", "monument", "historic"],
        "Heat Hazard": ["heat", "hot", "sun", "heatwave"],
        "Drain Blockage": ["drain", "sewage", "blockage", "overflow"]
    }
    
    category = "Other"
    found_cat_keyword = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                found_cat_keyword = kw
                break
        if category != "Other":
            break
            
    # Priority detection (Severity keywords)
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_urgent_keyword = ""
    
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            found_urgent_keyword = kw
            break
            
    # Flag nulls or ambiguity
    flag = ""
    if category == "Other" or not description.strip():
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason generation (Exactly one sentence citing specific words)
    if not description.strip():
        reason = "The description is empty, requiring manual review."
    elif flag == "NEEDS_REVIEW":
        reason = f"The description '{description[:30]}...' does not clearly match any defined category."
    else:
        reason = f"Classified as {category} because of '{found_cat_keyword}' and set to {priority} priority due to '{found_urgent_keyword if found_urgent_keyword else 'lack of urgent hazards'}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.
    Flags nulls, handles bad rows, and ensures output is produced.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Ensure complaint_id exists
                    if not row.get("complaint_id"):
                        row["complaint_id"] = "MISSING_ID"
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Not crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "ROW_ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Fatal error reading input: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Fatal error writing output: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

