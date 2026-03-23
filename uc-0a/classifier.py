"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import copy

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    location = row.get("location", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    text_to_search = f"{description} {location}"
    
    # Priority logic
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_severity = []
    for kw in severity_keywords:
        if kw in text_to_search:
            priority = "Urgent"
            matched_severity.append(kw)
            
    # Category logic
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging"],
        "Streetlight": ["streetlight", "light", "dark", "spark"],
        "Waste": ["garbage", "waste", "dump", "animal"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road surface cracked", "sinking", "manhole", "broken", "tyre damage", "footpath"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "drainage"]
    }
    
    matched_cats = []
    matched_cat_kw = []
    
    # Check text_to_search for keywords
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in text_to_search:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                matched_cat_kw.append(kw)
                
    ambiguous = False
    flag = ""
    
    if len(matched_cats) == 1:
        category = matched_cats[0]
    elif len(matched_cats) > 1:
        # Give precedence to Heritage Damage if mentioned explicitly
        if "Heritage Damage" in matched_cats and "heritage" in text_to_search:
            category = "Heritage Damage"
            ambiguous = False
        elif "Road Damage" in matched_cats and "Pothole" in matched_cats:
            category = "Pothole" # Specific pothole overrides generic road damage
            ambiguous = False
        else:
            category = "Other"
            ambiguous = True
    else:
        category = "Other"
        ambiguous = True
        
    if ambiguous:
        flag = "NEEDS_REVIEW"
        category = "Other"
        
    # Reason field MUST cite words from description
    reason_words = list(set(matched_cat_kw + matched_severity))
    if reason_words:
        reason = f"Classified based on keywords found: {', '.join(reason_words)}."
    elif not description:
        reason = "Empty description."
    else:
        reason = "No known category keywords matched."
        
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    
                    out_row = copy.deepcopy(row)
                    out_row["category"] = classification["category"]
                    out_row["priority"] = classification["priority"]
                    out_row["reason"] = classification["reason"]
                    out_row["flag"] = classification["flag"]
                    results.append(out_row)
                except Exception as e:
                    print(f"Warning: Failed to classify row {row.get('complaint_id', 'Unknown')}: {e}")
                    out_row = copy.deepcopy(row)
                    out_row["category"] = "Other"
                    out_row["priority"] = "Standard"
                    out_row["reason"] = f"Error processing: {str(e)}"
                    out_row["flag"] = "NEEDS_REVIEW"
                    results.append(out_row)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return
        
    if not results:
        print("No rows generated.")
        return
        
    fieldnames = list(results[0].keys())
    
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
