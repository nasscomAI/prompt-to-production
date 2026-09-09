"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAP = {
    "Pothole": ["pothole", "crater", "hole in the road"],
    "Flooding": ["flood", "waterlogged", "water level", "drowning"],
    "Streetlight": ["light", "dark", "bulb", "streetlamp", "streetlight"],
    "Waste": ["garbage", "trash", "waste", "dump", "rubbish"],
    "Noise": ["noise", "loud", "music", "construction sound"],
    "Road Damage": ["road", "crack", "pavement", "broken asphalt"],
    "Heritage Damage": ["heritage", "monument", "statue", "temple", "ruin"],
    "Heat Hazard": ["heat", "temperature", "sun", "stroke"],
    "Drain Blockage": ["drain", "sewer", "clog", "overflow"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    # Dynamically find the text description column
    description = row.get("description", row.get("text", list(row.values())[1] if len(row) > 1 else ""))
    
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "The description was empty or null.",
            "flag": "NEEDS REVIEW"
        }
        
    desc_lower = str(description).lower()
    
    # 1. Determine Priority
    matched_severity_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if matched_severity_words else "Standard"
    
    # 2. Determine Category
    matched_categories = []
    category_trigger_words = []
    
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                if cat not in matched_categories:
                    matched_categories.append(cat)
                category_trigger_words.append(kw)
                
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS REVIEW"
    else:
        category = "Other"
        if priority == "Standard":
            priority = "Low"
            
    # 3. Generate Reason
    words_to_cite = matched_severity_words + category_trigger_words
    if words_to_cite:
        cited = ", ".join(f"'{w}'" for w in set(words_to_cite))
        reason = f"Assigned {priority} priority and {category} category because the description mentions {cited}."
    else:
        reason = "Assigned default categorization as no specific keywords were detected."
        
    return {
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
    out_fieldnames = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            
            # Retain original columns and append new target columns
            out_fieldnames = list(reader.fieldnames or [])
            for col in ["category", "priority", "reason", "flag"]:
                if col not in out_fieldnames:
                    out_fieldnames.append(col)
                    
            for line_idx, row in enumerate(reader, start=2):
                try:
                    classification = classify_complaint(row)
                    row.update(classification)  # Merge results into the original row
                    results.append(row)
                except Exception as e:
                    row.update({
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing failed with error: {str(e)}",
                        "flag": "NEEDS REVIEW"
                    })
                    results.append(row)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found. Please check the path!")
        return

    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
