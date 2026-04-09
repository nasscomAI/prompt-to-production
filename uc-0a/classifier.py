import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "None"
    flag = ""
    
    # 1. Categorize based on keywords
    if "pothole" in desc or "cracked" in desc or "sinking" in desc:
        if "pothole" in desc:
            category = "Pothole"
        else:
            category = "Road Damage"
    elif "flood" in desc or "water" in desc:
        if "drain blocked" in desc or "drain block" in desc or "drain" in desc:
            category = "Drain Blockage"
        else:
            category = "Flooding"
    elif "streetlight" in desc or ("light" in desc and "out" in desc) or "dark" in desc:
        category = "Streetlight"
    elif "garbage" in desc or "waste" in desc or "animal" in desc or "smell" in desc:
        category = "Waste"
    elif "music" in desc or "noise" in desc:
        category = "Noise"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "footpath" in desc and "broken" in desc:
        category = "Road Damage"
        
    # Check for ambiguous cases
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 2. Assign priority based on severity keywords
    severity_keywords = [
        "injury", "child", "school", "hospital", 
        "ambulance", "fire", "hazard", "fell", "collapse"
    ]
    
    found_keywords = [kw for kw in severity_keywords if kw in desc]
    
    if found_keywords:
        priority = "Urgent"
        kw_str = ", ".join(found_keywords)
        reason = f"Urgent due to severity keywords: '{kw_str}'"
    else:
        if flag == "NEEDS_REVIEW":
            priority = "Low"
            reason = "Category is ambiguous and cannot be determined from description alone."
        else:
            reason = "Standard maintenance requested."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                print(f"Failed to process row {row.get('complaint_id')}: {e}")
                
    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
