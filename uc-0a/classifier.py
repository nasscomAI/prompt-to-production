"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

# Classification constants
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic that reflects the RICE rules.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    flag = ""
    
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description or "inaccessible" in description:
        if "drain" in description or "blocked" in description:
            category = "Drain Blockage"
        else:
            category = "Flooding"
    elif "light" in description:
        category = "Streetlight"
    elif any(kw in description for kw in ["garbage", "waste", "bins", "smell", "animal", "dumped"]):
        category = "Waste"
    elif any(kw in description for kw in ["noise", "music"]):
        category = "Noise"
    elif "heritage" in description:
        category = "Heritage Damage"
    elif any(kw in description for kw in ["road", "surface", "cracked", "sinking", "footpath", "tile", "manhole", "pavment"]):
        category = "Road Damage"
    elif "drain" in description:
        category = "Drain Blockage"
    elif "heat" in description or "hot" in description:
        category = "Heat Hazard"
    
    # Ambiguity check
    if category == "Other" or not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    # 2. Determine Priority
    priority = "Standard"
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if matched_severity:
        priority = "Urgent"
    elif int(row.get("days_open", 0)) > 14:
        priority = "Standard" # Just a filler, rule says Standard or Low
    else:
        priority = "Low"

    # 3. Generate Reason
    # Find which keyword triggered the categorization
    trigger_keyword = ""
    for kw in description.split():
        clean_kw = kw.strip(",.?!\"")
        if category.lower()[:4] in clean_kw.lower():
            trigger_keyword = clean_kw
            break
            
    if not trigger_keyword:
        # Fallback keyword detection
        all_kws = ["pothole", "flood", "water", "light", "garbage", "waste", "noise", "road", "surface", "drain", "manhole", "tile"]
        for kw in all_kws:
            if kw in description:
                trigger_keyword = kw
                break

    if category != "Other" and trigger_keyword:
        reason_cite = f"Categorized as {category} due to mentions of '{trigger_keyword}'"
    elif category != "Other":
        reason_cite = f"Categorized as {category} based on description context"
    else:
        reason_cite = "Description is ambiguous or does not match predefined categories"
        
    if priority == "Urgent":
        reason_cite += f" and flagged as Urgent because of '{matched_severity[0]}'."
    else:
        reason_cite += "."

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason_cite,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)
            
    if not results:
        print("No data processed.")
        return

    keys = results[0].keys()
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
