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
    desc = str(row.get('description', '')).lower()
    
    # Skill 2: Detect urgency keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "danger", "emergency"]
    found_urgent = [kw for kw in urgent_keywords if kw in desc]
    priority = "Urgent" if found_urgent else "Standard"
    
    # Skill 1: Classify complaint category
    cat_keywords = {
        "Pothole": ["pothole", "crater", "hole", "road damage", "crack"],
        "Flooding": ["flood", "flooding", "water", "drain", "waterlogging", "submerged"],
        "Streetlight Outage": ["streetlight", "street light", "outage", "dark", "bulb", "light"],
        "Trash Collection": ["trash", "garbage", "waste", "rubbish", "collection", "bin", "dump"]
    }
    
    matched_cat = None
    matched_word = None
    
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                matched_cat = cat
                matched_word = kw
                break
        if matched_cat:
            break
            
    reason_parts = []
    if matched_cat:
        category = matched_cat
        flag = ""
        reason_parts.append(f"Description mentions '{matched_word}'.")
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_parts.append("Could not determine specific category from description.")
        
    if found_urgent:
        reason_parts.append(f"Contains urgent keywords: {', '.join(found_urgent)}.")
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": " ".join(reason_parts),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
        
    if not results:
        print("No results to write.")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
