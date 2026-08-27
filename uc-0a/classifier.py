import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # RICE Enforcement 1: Category exact strings
    # Simple keyword mapping for local execution
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights out", "light"],
        "Waste": ["garbage", "waste", "dead animal", "dump"],
        "Noise": ["music", "noise"],
        "Road Damage": ["road surface cracked", "footpath", "broken", "crack"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "manhole"]
    }
    
    found_categories = set()
    matched_cat_words = []
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                found_categories.add(cat)
                matched_cat_words.append(kw)
    
    flag = ""
    category = "Other"
    
    if len(found_categories) == 1:
        category = list(found_categories)[0]
    elif len(found_categories) > 1:
        if "Heritage Damage" in found_categories and "Streetlight" in found_categories:
            category = "Other"
            flag = "NEEDS_REVIEW"
        elif "Flooding" in found_categories and "Drain Blockage" in found_categories:
            category = "Other"
            flag = "NEEDS_REVIEW"
        elif "Pothole" in found_categories and "Road Damage" in found_categories:
            category = "Pothole"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            
    # RICE Enforcement 2: Priority based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if kw in desc]
    
    if found_severity:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # RICE Enforcement 3: Reason explicitly citing specific words
    if found_severity:
        reason = f"Classified based on severity keyword '{found_severity[0]}'."
    elif matched_cat_words:
        reason = f"Classified based on description keyword '{matched_cat_words[0]}'."
    else:
        reason = "Classified as Other due to lack of distinct category keywords."
        
    if flag == "NEEDS_REVIEW":
        reason += " Description is ambiguous; flagged for review."

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
    """
    results = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if not row.get("complaint_id"):
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'Unknown')}: {e}")
                    
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return
        
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
