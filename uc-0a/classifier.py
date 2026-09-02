"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "hole in road", "road hole"],
    "Flooding": ["flood", "waterlogging", "water log", "submerge", "overflow"],
    "Streetlight": ["streetlight", "street light", "lamp", "light post", "no light"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dump", "litter"],
    "Noise": ["noise", "loud", "sound", "disturbance", "honking"],
    "Road Damage": ["road damage", "road crack", "road broken", "asphalt", "pavement"],
    "Heritage Damage": ["heritage", "monument", "historic", "heritage site", "ancient"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "heat stroke", "hot"],
    "Drain Blockage": ["drain", "sewer", "blockage", "clog", "sewage"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    if not description or description.strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    category = "Other"
    flag = ""
    matched_keywords = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keywords.append(kw)
                break
        if category != "Other":
            break
    
    if category == "Other" and not matched_keywords:
        flag = "NEEDS_REVIEW"
    
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break
    
    if matched_keywords:
        reason = f"Classified as {category} due to mention of '{matched_keywords[0]}' in the description."
    else:
        reason = f"No clear category keywords found; defaulted to Other."
    
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
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            results = []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error classifying: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return
    
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
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
