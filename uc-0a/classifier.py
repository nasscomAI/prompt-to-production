"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = {
    "Pothole": ["pothole", "crater", "hole"],
    "Flooding": ["flood", "waterlog", "water log"],
    "Streetlight": ["streetlight", "street light", "lamp", "dark"],
    "Waste": ["waste", "garbage", "trash", "dump"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road damage", "broken road", "surface", "crack"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat hazard", "temperature", "heatwave", "heat"],
    "Drain Blockage": ["drain", "blockage", "clog"]
}

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get("description", "")).lower()
    
    matched_category = "Other"
    cat_keyword_used = None
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in description:
                matched_category = cat
                cat_keyword_used = kw
                break
        if matched_category != "Other":
            break
            
    matched_priority = "Standard"
    sev_keyword_used = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            matched_priority = "Urgent"
            sev_keyword_used = kw
            break
            
    flag = "NEEDS_REVIEW" if matched_category == "Other" else ""
    
    reason_parts = []
    if cat_keyword_used:
        reason_parts.append(f"categorized based on '{cat_keyword_used}'")
    else:
        reason_parts.append("category could not be determined from description alone")
        
    if sev_keyword_used:
        reason_parts.append(f"marked urgent due to '{sev_keyword_used}'")
        
    reason = "Complaint " + " and ".join(reason_parts) + "."
    
    result = row.copy()
    result["category"] = matched_category
    result["priority"] = matched_priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            
            if not rows:
                print("Input CSV is empty.")
                return
                
            fieldnames = list(reader.fieldnames)
            for required_field in ["category", "priority", "reason", "flag"]:
                if required_field not in fieldnames:
                    fieldnames.append(required_field)
                
            classified_rows = []
            for row in rows:
                if not row.get("description") or not str(row.get("description")).strip():
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = "Empty description."
                    row["flag"] = "NEEDS_REVIEW"
                    classified_rows.append(row)
                    continue
                    
                processed_row = classify_complaint(row)
                classified_rows.append(processed_row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
            
    except Exception as e:
        print(f"Error processing batch: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
