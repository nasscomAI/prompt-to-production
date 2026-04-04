import argparse
import csv
import os
import sys

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "water"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["garbage", "waste", "dump", "animal", "smell", "trash", "bin"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["road surface", "footpath", "cracked", "tile", "sinking"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain", "manhole"]
}

def classify_complaint(row: dict) -> dict:
    """
    Transforms a single citizen complaint description into a structured classification
    consisting of a category, priority, justification, and review flag.
    """
    desc = row.get("description", "").lower()
    
    # Priority classification
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            break
            
    # Category and ambiguity classification
    matched_categories = []
    matched_kws = []
    
    for cat, kws in CATEGORY_MAPPING.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_kws.append(kw)
    
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        reason = "The description lacks known category keywords."
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        # Must be exactly one sentence and cite specific words
        reason = f"The description belongs to this category because it mentions the word '{matched_kws[0]}'."
    else:
        # Ambiguous case: genuinely ambiguous complaints must be flagged
        # Reject false confidence; ambiguous complaints must be flagged rather than forced into a category.
        # Ensure category is from ALLOWED_CATEGORIES
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason = f"This complaint is flagged as ambiguous because it mentions multiple keywords like '{matched_kws[0]}' and '{matched_kws[1]}'."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Orchestrates the end-to-end processing of a city-specific test file by reading input data
    and writing the final classified results to a CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        return
        
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Invalid CSV structure.")
                return
                
            for row in reader:
                classification = classify_complaint(row)
                
                # Check for taxonomy violation and missing justifications
                if classification["category"] not in ALLOWED_CATEGORIES:
                    print(f"Taxonomy violation: '{classification['category']}' is not an allowed category.")
                if not classification["reason"]:
                    print(f"Missing justification for complaint '{row.get('complaint_id')}'.")
                
                # Merge original row data with classification
                # Original columns + category, priority, reason, flag
                merged_row = row.copy()
                merged_row["category"] = classification["category"]
                merged_row["priority"] = classification["priority"]
                merged_row["reason"] = classification["reason"]
                merged_row["flag"] = classification["flag"]
                
                results.append(merged_row)
                
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return
        
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    try:
        # Output columns based on original plus the new ones
        out_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
