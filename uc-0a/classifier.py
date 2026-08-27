"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Priority
    priority = "Medium"
    urgent_keywords = ["injury", "child", "school", "dangerous", "safety"]
    for word in urgent_keywords:
        if word in desc:
            priority = "Urgent"
            break
            
    # Category and Reason
    category = "Other"
    flag = "NEEDS_REVIEW"
    reason = "No specific category keywords found."
    
    # Basic keyword mapping mimicking AI RICE rules
    if any(w in desc for w in ["pothole", "cracked", "sinking", "surface"]):
        category = "Pothole"
        flag = ""
        reason = f"Contains related words in description."
    elif any(w in desc for w in ["flood", "rain", "water", "drain"]):
        category = "Flooding"
        flag = ""
        reason = f"Contains related words in description."
    elif any(w in desc for w in ["light", "dark", "sparking"]):
        category = "Lighting"
        flag = ""
        reason = f"Contains related words in description."
    elif any(w in desc for w in ["music", "noise", "loud"]):
        category = "Noise"
        flag = ""
        reason = f"Contains related words in description."
    elif any(w in desc for w in ["vandal", "dumped", "waste"]):
        category = "Vandalism"
        flag = ""
        reason = f"Contains related words in description."
        
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
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Medium",
                "reason": f"Error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            
    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
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
