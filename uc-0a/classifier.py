"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine category rules safely
    category = "Other"
    cite = ""
    if "pothole" in description:
        category = "Pothole"
        cite = "pothole"
    elif "flood" in description:
        category = "Flooding"
        cite = "flood"
    elif "light" in description:
        category = "Streetlight"
        cite = "light"
    elif "garbage" in description or "waste" in description or "dead animal" in description:
        category = "Waste"
        cite = "waste/garbage"
    elif "music" in description or "noise" in description:
        category = "Noise"
        cite = "music"
    elif "crack" in description or "sinking" in description:
        category = "Road Damage"
        cite = "crack/sinking"
    elif "heritage" in description:
        category = "Heritage Damage"
        cite = "heritage"
    elif "drain" in description:
        category = "Drain Blockage"
        cite = "drain"
    
    # 2. Priority check
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            cite += f" & {kw}"
            break
            
    # 3. Flag check
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        cite = "unclear description"
        
    reason = f"Identified keywords: {cite}"
    
    row["category"] = category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            rows = list(reader)
            
            classified_rows = []
            for r in rows:
                classified_rows.append(classify_complaint(dict(r)))
                
        if not classified_rows:
             return
             
        with open(output_path, 'w', newline='', encoding='utf-8') as fout:
            fieldnames = list(classified_rows[0].keys())
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
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
