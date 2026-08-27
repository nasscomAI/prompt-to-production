"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "streetlight": "Streetlight",
    "lights out": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "dead animal": "Waste",
    "noise": "Noise",
    "music": "Noise",
    "road damage": "Road Damage",
    "road surface crack": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain block": "Drain Blockage"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    found_cat_keywords = []
    for key, val in CATEGORY_MAPPING.items():
        if key in desc:
            category = val
            found_cat_keywords.append(key)
            break # Take the first match
            
    # 2. Determine Priority
    priority = "Standard"
    found_sev_keywords = []
    for keyword in SEVERITY_KEYWORDS:
        # Match as whole word or partial, depending on needs. Let's do simple substring.
        if keyword in desc:
            priority = "Urgent"
            found_sev_keywords.append(keyword)
            
    if priority == "Standard" and "low" in desc:
         priority = "Low"
            
    # 3. Determine Reason
    reasons = []
    if found_cat_keywords:
        reasons.append(f"matched category keyword '{found_cat_keywords[0]}'")
    if found_sev_keywords:
        reasons.append(f"matched severity keyword '{found_sev_keywords[0]}'")
        
    if reasons:
        reason = f"Classified because description {' and '.join(reasons)}."
    else:
        reason = "No specific keywords found; assigned default classification."
        
    # 4. Determine Flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # Prepare result
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    if not rows:
        print("Input file is empty.")
        return

    fieldnames = list(rows[0].keys())
    for new_field in ["category", "priority", "reason", "flag"]:
        if new_field not in fieldnames:
            fieldnames.append(new_field)

    results = []
    for row in rows:
        if not row:
            continue
        try:
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            row_with_error = row.copy()
            row_with_error["category"] = "Other"
            row_with_error["priority"] = ""
            row_with_error["reason"] = f"Error during classification: {e}"
            row_with_error["flag"] = "NEEDS_REVIEW"
            results.append(row_with_error)

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
