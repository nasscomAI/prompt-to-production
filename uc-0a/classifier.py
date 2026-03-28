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
    complaint_id = row.get("complaint_id", row.get("id", ""))
    description = row.get("description", row.get("Description", ""))
    
    if not description or not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Complaint description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority check
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in desc_lower]
    
    if found_urgent:
        priority = "Urgent"
        priority_reason = f"severity keyword '{found_urgent[0]}'"
    else:
        priority = "Standard"
        priority_reason = "standard reporting"

    # Category check
    categories = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "water level"],
        "Streetlight": ["streetlight", "street light", "dark", "no light"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "litter"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["road damage", "crack", "broken road"],
        "Heritage Damage": ["heritage", "monument", "historic"],
        "Heat Hazard": ["heat hazard", "heat wave", "temperature"],
        "Drain Blockage": ["drain", "clog", "blockage", "sewer"]
    }
    
    category = "Other"
    cat_reason = "no specific keywords found"
    
    for cat, kws in categories.items():
        found_kw = next((kw for kw in kws if kw in desc_lower), None)
        if found_kw:
            category = cat
            cat_reason = f"keyword '{found_kw}'"
            break
            
    reason = f"Categorized as {category} based on {cat_reason} and marked {priority} due to {priority_reason}."
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
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
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fieldnames = list(reader.fieldnames)
                
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    # Append default error row
                    row.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": f"Processing error: {str(e)}", 
                        "flag": "NEEDS_REVIEW"
                    })
                    results.append(row)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    if not fieldnames:
        print("Empty or invalid input CSV.")
        return

    expected_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    for field in expected_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
