"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlog", "submerge", "water"],
    "Streetlight": ["streetlight", "light", "dark", "sparking"],
    "Waste": ["waste", "garbage", "trash", "dump", "animal"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["crack", "road", "pavement", "sink", "tile", "manhole"],
    "Heritage Damage": ["heritage", "monument", "fort"],
    "Heat Hazard": ["heat", "hot", "sun"],
    "Drain Blockage": ["drain", "clog", "sewage", "block"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict representing the row with classification fields added.
    """
    description = str(row.get('description', '')).lower()
    
    # Priority Enforcement
    found_severity_kws = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    priority = "Urgent" if found_severity_kws else "Standard"
    
    # Category Enforcement
    matched_categories = []
    matched_category_kws = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                if category not in matched_categories:
                    matched_categories.append(category)
                matched_category_kws.append(kw)
    
    # Ambiguity Enforcement
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Genuinely ambiguous (0 or >1 matches)
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason Enforcement (one sentence, citing specific words)
    if found_severity_kws:
        reason = f"Classified as {category} with {priority} priority citing severity keywords: {', '.join(found_severity_kws)}."
    elif matched_category_kws:
        reason = f"Classified as {category} citing descriptive keywords: {', '.join(matched_category_kws)}."
    else:
        reason = "Classified as Other due to lack of distinct recognizable keywords in the description."
        
    # Create the output row preserving original data
    output_row = row.copy()
    output_row["category"] = category
    output_row["priority"] = priority
    output_row["reason"] = reason
    output_row["flag"] = flag
    
    return output_row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely handles bad rows and ensures all valid classifications are written.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                print("Error: Input CSV has no header.")
                return
            
            # Prepare new fieldnames in output sequence
            new_fields = ["category", "priority", "reason", "flag"]
            out_fieldnames = list(reader.fieldnames) + [f for f in new_fields if f not in reader.fieldnames]

            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                
                success_count = 0
                for i, row in enumerate(reader, start=1):
                    try:
                        classified_row = classify_complaint(row)
                        writer.writerow(classified_row)
                        success_count += 1
                    except Exception as e:
                        row_id = row.get("complaint_id", f"row-{i}")
                        print(f"Warning: Failed to process '{row_id}'. Reason: {e}")
                        
        print(f"Successfully classified {success_count} rows.")
    except Exception as e:
        print(f"Fatal Error processing batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
