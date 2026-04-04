"""
UC-0A — Complaint Classifier
Implemented using the RICE → agents.md → skills.md constraints.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE constraints defined in agents.md.
    Returns: dict with all original keys plus category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority Keywords check
    priority_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_priority_keywords = [kw for kw in priority_keywords if kw in desc]
    
    if found_priority_keywords:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Category mapping check using explicit string mapping
    category_mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "animal": "Waste",
        "dump": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road": "Road Damage",
        "cracked": "Road Damage",
        "footpath": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "manhole": "Drain Blockage",
    }
    
    found_categories = set()
    matched_keyword = None
    
    for kw, cat in category_mapping.items():
        if kw in desc:
            found_categories.add(cat)
            if not matched_keyword:
                matched_keyword = kw
                
    if len(found_categories) == 1:
        category = list(found_categories)[0]
        flag = ""
        reason_part = f'Classified as {category} because description contains "{matched_keyword}"'
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(found_categories) > 1:
            reason_part = f'Ambiguous classification; multiple keywords found like "{matched_keyword}"'
        else:
            reason_part = f'No clear category keywords found in description'
            
    # Include priority reason if Urgent
    if priority == "Urgent":
        reason_part += f' and marked Urgent due to keyword "{found_priority_keywords[0]}"'

    # Ensure strictly one complete sentence for the enforcement rule
    reason = reason_part + "."
        
    # Clone the row and add our new fields
    output_row = row.copy()
    output_row["category"] = category
    output_row["priority"] = priority
    output_row["reason"] = reason
    output_row["flag"] = flag
    
    return output_row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle errors gracefully and write a PROCESSING_ERROR flag if exception occurs.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                fieldnames = []
                
            out_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        classified_row = classify_complaint(row)
                        writer.writerow(classified_row)
                    except Exception as e:
                        print(f"Error classifying row {row.get('complaint_id', 'Unknown')}: {e}")
                        error_row = row.copy()
                        error_row["category"] = "Other"
                        error_row["priority"] = "Standard"
                        error_row["reason"] = "Failed to process row due to internal error."
                        error_row["flag"] = "PROCESSING_ERROR"
                        writer.writerow(error_row)
    except Exception as e:
        print(f"Failed processing batch: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
