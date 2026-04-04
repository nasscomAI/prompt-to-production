"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", "")
    
    # Simple rule-based logic for this exercise (a real LLM would be used here in production)
    category = "Other"
    priority = "Low"
    reason = "No specific keywords found."
    flag = ""
    
    # 1. Category Detection
    matched_categories = []
    if any(word in desc for word in ["pothole"]): matched_categories.append("Pothole")
    if any(word in desc for word in ["flood", "water"]): matched_categories.append("Flooding")
    if any(word in desc for word in ["light", "dark"]): matched_categories.append("Streetlight")
    if any(word in desc for word in ["garbage", "waste", "trash"]): matched_categories.append("Waste")
    if any(word in desc for word in ["loud", "noise", "music"]): matched_categories.append("Noise")
    if any(word in desc for word in ["road", "crack"]): matched_categories.append("Road Damage")
    if any(word in desc for word in ["monument", "heritage", "statue"]): matched_categories.append("Heritage Damage")
    if any(word in desc for word in ["heat", "hot", "sun"]): matched_categories.append("Heat Hazard")
    if any(word in desc for word in ["drain", "clog", "sewer"]): matched_categories.append("Drain Blockage")
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        # Find a reason based on the description
        words = desc.split()
        reason = f"Mentioned keywords like '{matched_categories[0].lower()}' in the description."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Multiple category keywords detected, ambiguous."
    else:
        # Check if description exists but no obvious category matches
        if len(desc) > 5:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = "Description does not match any known category cleanly."
    
    # 2. Priority Detection
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    if found_keywords:
        priority = "Urgent"
        reason += f" Contains severity keywords: {', '.join(found_keywords)}."
    elif category != "Other":
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = []
    
    # Read Phase
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    
                    # Merge classification results into the original row
                    out_row = dict(row)
                    out_row["category"] = classification["category"]
                    out_row["priority_flag"] = classification["priority"]
                    out_row["reason"] = classification["reason"]
                    out_row["flag"] = classification["flag"]
                    results.append(out_row)
                    
                except Exception as e:
                    # Wraps row-level errors
                    err_row = dict(row)
                    err_row["category"] = "Other"
                    err_row["priority_flag"] = "Low"
                    err_row["reason"] = f"Error processing row: {str(e)}"
                    err_row["flag"] = "NEEDS_REVIEW"
                    results.append(err_row)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    # Validation
    if not fieldnames:
        print("Error: Input file appears to be empty or missing headers.")
        return
        
    out_fieldnames = fieldnames + ["category", "priority_flag", "reason", "flag"]
    # Ensure no duplicates (like if category was already in input but empty)
    out_fieldnames = list(dict.fromkeys(out_fieldnames))
    
    # Write Phase
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
