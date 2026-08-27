"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if found_severity else "Standard"
    
    # 2. Determine category
    category = "Other"
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "rain" in desc:
        category = "Flooding"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "animal" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
    elif "road" in desc and ("crack" in desc or "surface" in desc):
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc or "block" in desc:
        category = "Drain Blockage"
        
    # Overrides based on testing
    if "heritage" in desc:
        category = "Heritage Damage"
    if "flood" in desc and "drain blocked" in desc:
        category = "Flooding"
    if "drain blocked" in desc.replace("blocked", "block"):
        category = "Drain Blockage"
        
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 3. Create reason
    if found_severity:
        reason = f"Classified as {category} and {priority} because description contains '{found_severity[0]}'."
    else:
        # Provide a generic keyword for reason if no severity word
        reason = f"Classified as {category} based on keywords in description."
        
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
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                if not row.get("description"):
                    # Handle nulls
                    res = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Null description provided.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id')}: {e}")
                
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
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
