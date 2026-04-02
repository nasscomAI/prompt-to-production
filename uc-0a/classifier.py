"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # 1. Map to Category
    category_mapping = {
        "pothole": "Pothole",
        "crater": "Pothole",
        "flood": "Flooding",
        "rain": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "dump": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "crack": "Road Damage",
        "sinking": "Road Damage",
        "damage": "Road Damage",
        "broken": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "block": "Drain Blockage"
    }
    
    assigned_category = "Other"
    for key, cat in category_mapping.items():
        if key in desc_lower:
            assigned_category = cat
            break
            
    flag = ""
    # Flag review if category is Other/ambiguous
    if assigned_category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 2. Evaluate Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for uk in urgent_keywords:
        if uk in desc_lower:
            priority = "Urgent"
            break
            
    # 3. Extract Reason
    sentences = [s.strip() for s in description.split(".") if s.strip()]
    if sentences:
        first_sentence = sentences[0]
        reason = f"The description states '{first_sentence}' which justifies this classification."
    else:
        reason = "The description provided no sufficient text to formulate a reason."

    return {
        "complaint_id": row.get("complaint_id", ""),
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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    # Do not crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find '{input_path}'")
        sys.exit(1)
        
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
