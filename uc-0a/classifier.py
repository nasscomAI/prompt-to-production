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
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = str(description).lower()
    
    # Priority logic
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    priority_word = None
    
    for word in severity_keywords:
        if word in desc_lower:
            priority = "Urgent"
            priority_word = word
            break
            
    if priority == "Standard":
        if any(w in desc_lower for w in ["minor", "slight", "small"]):
            priority = "Low"
            priority_word = "minor"
    
    # Category logic
    categories = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "water", "overflow"],
        "Streetlight": ["light", "dark", "streetlamp", "streetlight"],
        "Waste": ["waste", "garbage", "trash", "rubbish"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["crack", "road", "surface"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "sun"],
        "Drain Blockage": ["drain", "clog", "blockage", "blocked"]
    }
    
    category = "Other"
    category_word = None
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                category_word = kw
                break
        if category != "Other":
            break
            
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # Reason logic
    reason_parts = []
    if category_word:
        reason_parts.append(f"contains the word '{category_word}' indicating {category}")
    else:
        reason_parts.append("category could not be confidently determined from the description alone")
        
    if priority_word:
        reason_parts.append(f"priority is {priority} because it mentions '{priority_word}'")
    else:
        reason_parts.append(f"priority is {priority}")
        
    reason = "The description " + " and ".join(reason_parts) + "."
    
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Failed to process row due to error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })

    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        try:
            with open(output_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
