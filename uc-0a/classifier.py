"""
Rule-Based Complaint Classifier (UC-0A)
Processes complaint CSV files locally using standard Python libraries.
No external API or AI service is used.
"""
import argparse
import csv
import os
import re

from typing import Dict, List, Tuple

# 1. Classification Schema: Exact Categories
ALLOWED_CATEGORIES: List[str] = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# 2. Agent Skills and Keyword Mapping
# Ordered specifically. Highest priority categories matched first (e.g Heritage before Streetlight)
CATEGORY_RULES: Dict[str, List[str]] = {
    "Pothole": ["pothole", "cracked", "tyre damage"],
    "Heritage Damage": ["heritage"],
    "Flooding": ["flooded", "water", "rain", "floods", "accumulation", "rainfall"],
    "Streetlight": ["streetlight", "lights out", "dark", "sparking"],
    "Waste": ["waste", "garbage", "trash", "dumped", "animal"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["road surface", "sinking", "crack", "broken", "surface", "cracks"],
    "Drain Blockage": ["drain", "blockage", "blocked", "manhole"],
    "Heat Hazard": ["heat", "temperature"]
}

# 3. Severity Keywords for Priority mapping
SEVERITY_KEYWORDS: List[str] = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    """
    Apply rule-based conditions to classify a single complaint row.
    Returns: (category, priority, reason, flag)
    """
    # Returns: (category, priority, reason, flag)
    #
    description_val = row.get("description", "")
    description_lower: str = str(description_val).lower() if description_val else ""

    assigned_category: str = "Other"
    assigned_priority: str = "Standard"
    flag: str = "NEEDS_REVIEW"
    matched_category_keyword = None
    matched_severity_keyword = None
    
    # Check for Priority Severity Match
    for keyword in SEVERITY_KEYWORDS:
        if re.search(re.escape(keyword), description_lower):
            assigned_priority = "Urgent"
            matched_severity_keyword = keyword
            break

        # Check for Category Match
        found_category = False
        for category, keywords in CATEGORY_RULES.items():
            for keyword in keywords:
                # Handle whole word matching for exactness
                if re.search(re.escape(keyword), description_lower):
                    assigned_category = category
                    matched_category_keyword = keyword
                    flag = ""  # Clear flag if we have a definitive match
                    found_category = True
                    break
            if found_category:
                break

    # If still 'Other', perform secondary fallback check against strict ALLOWED_CATEGORIES names
    if assigned_category == "Other":
        for allowed_cat in ALLOWED_CATEGORIES:
            # Skip 'Other'
            if allowed_cat == "Other":
                continue
                
            # Perform direct substring search of the category name
            if re.search(re.escape(allowed_cat.lower()), description_lower):
                assigned_category = allowed_cat
                matched_category_keyword = allowed_cat.lower()
                flag = ""
                break
                
    # Construct the citation reason
    reasons = []
    if matched_category_keyword:
        reasons.append(f"Keyword '{matched_category_keyword}' determined category {assigned_category}.")
    if matched_severity_keyword:
        reasons.append(f"Severity keyword '{matched_severity_keyword}' triggered Urgent priority.")
        
    if not reasons:
        reason = "No specific keywords found, defaulted to Other."
    else:
        reason = " ".join(reasons)

    return assigned_category, assigned_priority, reason, flag

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classification rules, and write output CSV.
    Output Columns exactly: complaint_id, date_raised, city, ward, location, description, reported_by, days_open, category, priority, reason, flag
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Input CSV is empty or missing headers.")
                return
            rows = list(reader)
    except Exception as e:
        print(f"Failed to read {input_path}: {e}")
        return

    # Prepare standard output headers exactly as specified
    expected_headers = [
        "complaint_id", "date_raised", "city", "ward", "location", 
        "description", "reported_by", "days_open", "category", 
        "priority", "reason", "flag"
    ]
    
    # Remove priority_flag if it exists inside the raw data headers
    if fieldnames is not None:
        field_list: List[str] = list(fieldnames)
        try:
            field_list.remove("priority_flag")
        except ValueError:
            pass
        fieldnames = field_list
    
    # Order columns based on expected_headers constraints
    out_fieldnames = []
    for header in expected_headers:
        if header in fieldnames or header in ["category", "priority", "reason", "flag"]:
            out_fieldnames.append(header)
    for header in fieldnames: # Catch any trailing unexpected ones
        if header not in out_fieldnames:
            out_fieldnames.append(header)

    results: List[Dict[str, str]] = []
    for index, row in enumerate(rows):
        # Allow typing dict as fully mutated structure
        clean_row: Dict[str, str] = {}
        for k, v in row.items():
            if k in out_fieldnames or k == "description":
                clean_row[k] = v
        
        # Apply the rule-based agent logic
        category, priority, reason, flag = classify_complaint(clean_row)
        
        # Add new columns as output
        clean_row["category"] = category
        clean_row["priority"] = priority
        clean_row["reason"] = reason
        clean_row["flag"] = flag
        
        # ensure no key error when exporting
        result_row: Dict[str, str] = {}
        for k in out_fieldnames:
            result_row[k] = clean_row.get(k, "")
        results.append(result_row)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} rows. Results written to {output_path}")
    except Exception as e:
        print(f"Failed to write {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Rule-Based Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input test CSV file")
    parser.add_argument("--output", required=True, help="Path to output results CSV file")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
    else:
        batch_classify(args.input, args.output)
