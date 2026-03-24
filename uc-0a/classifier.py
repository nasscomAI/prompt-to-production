"""
UC-0A — Complaint Classifier
Implemented using purely built-in Python packages.
Uses rule-based text matching to follow RICE framework guidelines.
"""
import argparse
import csv
import re
import os

# Define the taxonomy mappings to keywords (lowercased)
TAXONOMY_MAP = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded"],
    "Streetlight": ["streetlight", "lights out", "dark at night"],
    "Waste": ["garbage", "waste", "smell", "dumped", "dead animal"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["cracked", "sinking", "broken", "road surface", "tiles broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "temperature"],
    "Drain Blockage": ["drain blocked", "drainage", "drain"],
}

# Severity keywords mapping to Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using standard string matching rules.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # Identify Categories
    matched_categories = []
    category_reasons = []
    
    for category, keywords in TAXONOMY_MAP.items():
        for kw in keywords:
            if kw in description:
                if category not in matched_categories:
                    matched_categories.append(category)
                    category_reasons.append(kw)
    
    # Priority Resolution (default to Low unless we see severity keywords)
    priority = "Low"
    priority_reason_word = None
    
    for sev_kw in SEVERITY_KEYWORDS:
        if sev_kw in description:
            priority = "Urgent"
            priority_reason_word = sev_kw
            break
            
    # Resolve Priority and Base Reason
    # We elevate priority to Standard if it's not urgent but matches a category
    if priority != "Urgent" and matched_categories:
        priority = "Standard"
        
    # Formatting output according to Enforcement guidelines
    out_flag = ""
    out_category = ""
    out_reason = ""
    
    if len(matched_categories) == 1:
        out_category = matched_categories[0]
        base_word = category_reasons[0]
        
        if priority == "Urgent":
            out_reason = f"Classified as {out_category} and Urgent because the description mentions '{base_word}' and '{priority_reason_word}'."
        else:
            out_reason = f"Classified as {out_category} because the description mentions '{base_word}'."
            
    elif len(matched_categories) > 1:
        # Ambiguous category - matches multiple categories
        out_category = "Other"
        out_flag = "NEEDS_REVIEW"
        out_reason = f"Category is ambiguous due to mentions of conflicting terms: {', '.join(category_reasons)}."
    else:
        # No categories matched
        out_category = "Other"
        out_flag = "NEEDS_REVIEW"
        out_reason = "No recognized taxonomy keywords were found in the description."

    return {
        "category": out_category,
        "priority": priority,
        "reason": out_reason,
        "flag": out_flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    print(f"Reading from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fn = reader.fieldnames
            if fn is None:
                print("Error: Input CSV is empty.")
                return
            fieldnames = list(fn) + ['category', 'priority', 'reason', 'flag']
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
        
    print(f"Found {len(rows)} rows to classify. Writing to {output_path}...")
    
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, row in enumerate(rows):
                cid = row.get('complaint_id', f'Row_{i+1}')
                classification = classify_complaint(row)
                out_row = {**row, **classification}
                writer.writerow(out_row)
    except Exception as e:
        print(f"Error writing to output file: {e}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Batch classification complete.")
