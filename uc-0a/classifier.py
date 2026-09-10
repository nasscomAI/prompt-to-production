import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    text = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    # Categories
    categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
    ]
    
    assigned_category = "Other"
    for cat in categories:
        if cat.lower() in text:
            assigned_category = cat
            break
            
    # Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_keyword = None
    for kw in urgent_keywords:
        if kw in text:
            priority = "Urgent"
            found_keyword = kw
            break
            
    # Reason
    if found_keyword:
        reason = f"Urgent priority due to keyword '{found_keyword}'."
    elif assigned_category != "Other":
        reason = f"Classified as {assigned_category} based on description."
    else:
        reason = "Unable to find specific keywords."
        
    # Flag
    flag = ""
    if assigned_category == "Other" or len(text.strip()) < 10:
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
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
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception:
                    # Do not crash on bad rows
                    pass
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if not results:
        print("No results to write.")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
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
