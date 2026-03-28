import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower() if description else ""
    
    # 1. Enforcement rule: Priority logic based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", 
                         "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    triggered_kw = None
    
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            triggered_kw = kw
            break
            
    # 2. Enforcement rule: Category mapping to strictly predefined strings
    category = "Other"
    cat_kw = None
    
    if "pothole" in desc_lower:
        category, cat_kw = "Pothole", "pothole"
    elif "flood" in desc_lower or "rain" in desc_lower or "water" in desc_lower:
        category, cat_kw = "Flooding", "flood"
    elif "streetlight" in desc_lower or "light" in desc_lower or "dark" in desc_lower:
        category, cat_kw = "Streetlight", "streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "dump" in desc_lower or "animal" in desc_lower:
        category, cat_kw = "Waste", "waste"
    elif "noise" in desc_lower or "music" in desc_lower:
        category, cat_kw = "Noise", "noise"
    elif "crack" in desc_lower or "sink" in desc_lower or "footpath" in desc_lower or "manhole" in desc_lower:
        category, cat_kw = "Road Damage", "road damage"
    elif "heritage" in desc_lower:
        category, cat_kw = "Heritage Damage", "heritage"
    elif "heat" in desc_lower:
        category, cat_kw = "Heat Hazard", "heat"
    elif "drain" in desc_lower or "block" in desc_lower:
        category, cat_kw = "Drain Blockage", "drain"
        
    # 3. Refusal condition: If genuinely ambiguous, flag it
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 4. Reason field: Exactly one sentence citing specific words
    reason_word = triggered_kw if priority == "Urgent" else cat_kw
    if reason_word:
        reason = f"The description highlights an issue classified by the keyword '{reason_word}'."
    else:
        reason = "The description lacks known definitive keywords to assign a specific category."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row using classify_complaint, write results CSV.
    Safely handles bad rows and ensures the process completes.
    """
    in_rows = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            for row in reader:
                in_rows.append(row)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return
        
    new_fields = ["category", "priority", "reason", "flag"]
    out_fieldnames = fieldnames + [f for f in new_fields if f not in fieldnames]
    
    results = []
    for row in in_rows:
        try:
            # Handle null descriptions safely without crashing
            if "description" not in row or row["description"] is None:
                row["description"] = ""
                
            classified = classify_complaint(row)
            row.update(classified)
            results.append(row)
        except Exception as e:
            row["category"] = "Other"
            row["priority"] = "Standard"
            row["reason"] = f"Error during classification logic: {str(e)}"
            row["flag"] = "NEEDS_REVIEW"
            for f in new_fields:
                if f not in row:
                    row[f] = ""
            results.append(row)
            
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
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
    print(f"Done. Results written to {args.output}")
