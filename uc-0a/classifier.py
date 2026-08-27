"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os
import re

# Allowed Categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity Keywords for Urgent Priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "")
    if description is None:
        description = ""
    
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    category = "Other"
    priority = "Standard"
    reason = "No specific category keywords found."
    flag = ""

    # 1. Determine Category
    category_mapping = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "submerged"],
        "Streetlight": ["streetlight", "light", "unlit", "darkness"],
        "Waste": ["garbage", "waste", "bin", "trash", "dumped", "animal", "refuse"],
        "Noise": ["noise", "music", "loud", "audible", "sound"],
        "Road Damage": ["road surface", "cracked", "sinking", "pavement", "footpath", "tile", "tarmac", "subsidence", "paving"],
        "Heritage Damage": ["heritage", "ancient", "monument", "historic"],
        "Heat Hazard": ["heat", "temperature", "melting", "degrees", "unbearable", "burn", "sun", "heatwave"],
        "Drain Blockage": ["drain", "manhole", "sewage", "gutter"],
    }

    found_categories = []
    found_keywords = []
    
    for cat, keywords in category_mapping.items():
        for kw in keywords:
            # Match whole words to avoid issues like 'sun' in 'Sunday'
            if re.search(rf'\b{re.escape(kw)}\b', desc_lower):
                if cat not in found_categories:
                    found_categories.append(cat)
                    found_keywords.append(kw)
                break
    
    if len(found_categories) == 1:
        category = found_categories[0]
        reason = f"Category identified because description mentions '{found_keywords[0]}'."
    elif len(found_categories) > 1:
        # Ambiguous case: multiple categories matched
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous: multiple categories matched ({', '.join(found_categories)})."
    else:
        # No category matched
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Genuinely ambiguous: no specific keywords found in description."

    # 2. Determine Priority
    found_severity = []
    for kw in SEVERITY_KEYWORDS:
        # Match whole word or prefix (e.g., 'child' in 'children', 'injur' in 'injury')
        if re.search(rf'\b{re.escape(kw)}', desc_lower):
            found_severity.append(kw)
    
    if found_severity:
        priority = "Urgent"
        reason += f" Priority set to Urgent due to keywords: {', '.join(found_severity)}."
    else:
        priority = "Standard"

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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Check for nulls/empty description
                    desc = row.get("description")
                    if desc is None or not desc.strip():
                        result = {
                            "complaint_id": row.get("complaint_id", "UNKNOWN"),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Missing or null description.",
                            "flag": "NEEDS_REVIEW"
                        }
                    else:
                        result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Per-row error handling
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
