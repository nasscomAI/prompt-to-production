"""
UC-0A — Complaint Classifier
Implemented based on agents.md and skills.md.
"""
import argparse
import csv

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    priority = "Standard"
    reason_keyword = "routine"
    
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            reason_keyword = kw
            break
            
    category = "Other"
    cat_keyword = "unclear"
    
    if "pothole" in desc:
        category = "Pothole"
        cat_keyword = "pothole"
    elif "flood" in desc or "rain" in desc:
        category = "Flooding"
        cat_keyword = "flood"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        cat_keyword = "light"
    elif "waste" in desc or "garbage" in desc or "animal" in desc:
        category = "Waste"
        cat_keyword = "waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        cat_keyword = "noise"
    elif ("road" in desc and ("crack" in desc or "sink" in desc)) or "manhole" in desc:
        category = "Road Damage"
        cat_keyword = "road damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
        cat_keyword = "heritage"
    elif "drain" in desc:
        category = "Drain Blockage"
        cat_keyword = "drain"
        
    reason = f"Classified as {category} with {priority} priority because the description mentions '{cat_keyword}' and severity indicator '{reason_keyword}'."
    
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Genuinely ambiguous complaint; marked for review."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames
        
    out_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
    
    out_rows = []
    for row in rows:
        try:
            # Skip empty rows visually
            if not row.get("description"):
                continue
            classification = classify_complaint(row)
            row.update(classification)
            out_rows.append(row)
        except Exception as e:
            row["flag"] = "NEEDS_REVIEW"
            row["reason"] = f"Error processing row: {e}"
            row["category"] = "Other"
            row["priority"] = "Low"
            out_rows.append(row)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
