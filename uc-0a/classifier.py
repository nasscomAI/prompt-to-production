"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md requirements.
"""
import argparse
import csv
import os
import re

# Taxonomy from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords from agents.md
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint based on text description.
    Follows strict taxonomy and keyword-based priority rules.
    """
    desc_lower = description.lower()
    
    # 1. Ambiguity check / Error handling (Empty or too short)
    if not description or len(description.strip()) < 5:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or too short to classify.",
            "flag": "NEEDS_REVIEW"
        }

    # 2. Category logic (Naive keyword matching for this workshop context)
    category = "Other"
    flag = ""
    
    # Mapping keywords to categories
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "water": "Flooding",
        "light": "Streetlight",
        "garbage": "Waste",
        "trash": "Waste",
        "waste": "Waste",
        "noise": "Noise",
        "sound": "Noise",
        "road": "Road Damage",
        "damage": "Road Damage",
        "heritage": "Heritage Damage",
        "monument": "Heritage Damage",
        "heat": "Heat Hazard",
        "hot": "Heat Hazard",
        "drain": "Drain Blockage",
        "blockage": "Drain Blockage"
    }

    found_categories = []
    for key, val in category_map.items():
        if key in desc_lower:
            found_categories.append(val)
    
    # Check for ambiguity
    if len(set(found_categories)) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat = f"Ambiguous due to multiple potential categories ({', '.join(set(found_categories))})."
    elif len(found_categories) == 1:
        category = found_categories[0]
        reason_cat = f"Identified as {category} based on keywords in description."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat = "No clear category keyword found."

    # 3. Priority logic (Severity keyword matching)
    priority = "Standard"
    triggered_keywords = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    
    if triggered_keywords:
        priority = "Urgent"
        reason_pri = f"Priority set to Urgent due to keywords: {', '.join(triggered_keywords)}."
    else:
        # Default logic for Standard vs Low could be added here
        priority = "Standard"
        reason_pri = "No severity keywords found; defaulting to Standard."

    # Combine reason into one sentence as per agents.md
    combined_reason = f"{reason_cat} {reason_pri}"
    
    return {
        "category": category,
        "priority": priority,
        "reason": combined_reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, applies classification, and writes results to CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            rows_processed = 0
            results = []
            
            for row in reader:
                # We assume description is in a column named 'description' or similar
                # If column names vary, we look for common ones
                desc_col = next((col for col in reader.fieldnames if col.lower() in ['description', 'text', 'complaint']), None)
                
                description = row.get(desc_col, "")
                classification = classify_complaint(description)
                
                row.update(classification)
                results.append(row)
                rows_processed += 1

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Successfully processed {rows_processed} rows.")

    except Exception as e:
        print(f"An error occurred during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
