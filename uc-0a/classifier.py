"""
UC-0A — Complaint Classifier
Rule-based heuristic implementation (No LLM).
"""
import argparse
import csv
import os

# Categories allowed
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Urgent keywords
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Heuristics for categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole"],
    "Flooding": ["flood", "waterlogging", "water logged", "submerged", "drown"],
    "Streetlight": ["streetlight", "street light", "lamp", "bulb", "dark", "unlit"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "bin", "litter"],
    "Noise": ["noise", "loud", "speaker", "music", "dj", "yell"],
    "Road Damage": ["road damage", "crack", "broken road", "pavement"],
    "Heritage Damage": ["heritage", "monument", "historic", "statue", "fort"],
    "Heat Hazard": ["heat", "hot", "sun", "boiling", "temperature"],
    "Drain Blockage": ["drain", "clog", "gutter", "sewer", "block"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using heuristic rules.
    Returns: dict with keys updated: category, priority, reason, flag
    """
    # Find text to analyze
    # Assuming 'description' is the main field, fallback to checking all string values
    text = row.get("description", "")
    if not text:
        # If no description column, combine all values
        text = " ".join(str(v) for v in row.values() if v)
        
    text_lower = text.lower()
    
    # 1. Determine Priority
    urgent_words_found = [kw for kw in URGENT_KEYWORDS if kw in text_lower]
    if urgent_words_found:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # 2. Determine Category
    matched_categories = []
    category_words_found = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                category_words_found.append(kw)
                
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 3. Construct Reason
    reason_parts = []
    if category_words_found:
        reason_parts.append(f"mentions '{category_words_found[0]}'")
    else:
        reason_parts.append("lacks clear category keywords")
        
    if urgent_words_found:
        reason_parts.append(f"contains severe keywords like '{urgent_words_found[0]}'")
        
    reason = f"Classified as {category} with {priority} priority because the description {' and '.join(reason_parts)}."
    
    output = row.copy()
    output['category'] = category
    output['priority'] = priority
    output['reason'] = reason
    output['flag'] = flag
    
    return output

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return
        
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            output_fieldnames = list(fieldnames)
            for field in ['category', 'priority', 'reason', 'flag']:
                if field not in output_fieldnames:
                    output_fieldnames.append(field)
            
            for i, row in enumerate(reader):
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Error classifying row {i+1}: {e}")
                    failed_row = row.copy()
                    failed_row['category'] = 'Other'
                    failed_row['priority'] = 'Standard'
                    failed_row['reason'] = f"Failed to parse row: {e}"
                    failed_row['flag'] = 'NEEDS_REVIEW'
                    results.append(failed_row)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)
            print(f"Successfully processed {len(results)} rows and saved to {output_path}")
            
    except Exception as e:
        print(f"Error during batch classification: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (Rule-based)")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

