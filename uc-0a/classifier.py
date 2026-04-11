"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAP = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlog", "rain", "water"],
    "Streetlight": ["light", "dark", "lamp"],
    "Waste": ["garbage", "trash", "waste", "dump", "litter", "debris"],
    "Noise": ["noise", "loud", "sound", "speaker", "music", "honking"],
    "Road Damage": ["road", "pavement", "asphalt", "shattered", "crack"],
    "Heritage Damage": ["heritage", "monument", "statue", "old", "historic"],
    "Heat Hazard": ["heat", "hot", "sun", "shelter", "shade"],
    "Drain Blockage": ["drain", "sewage", "gutter", "block", "choke"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agents.md enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    category = "Other"
    reason_keyword = ""
    
    # Category Assignment (Keyword-based simulation of taxonomy mapping)
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in description:
                category = cat
                reason_keyword = kw
                break
        if category != "Other":
            break
            
    # Priority Assignment (Strict rule from agents.md)
    priority = "Low"
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if found_severity:
        priority = "Urgent"
        reason_keyword = found_severity[0] # Use the severity keyword for the reason
    elif any(kw in description for kw in ["dangerous", "risk", "broken", "damage"]):
        priority = "Standard"
        
    # Reason Generation (Strict citation rule)
    if category == "Other" and not found_severity:
        reason = "The description does not contain specific keywords mapping to a predefined category."
    else:
        # Construct a simple sentence citing the description
        reason = f"Classified based on the mention of '{reason_keyword}' which indicates a {category.lower()} issue with {priority.lower()} priority."

    # Flag Assignment (Strict rule from agents.md)
    flag = ""
    if category == "Other" or not description.strip():
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category cannot be determined from description alone; requires manual review."

    return {
        **row,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Ensures robustness as per skills.md.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            results = []
            for row in reader:
                # Handle nulls/bad rows by ensuring description exists
                if not row or not any(row.values()):
                    continue
                
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Failed to process row {row.get('complaint_id')}: {e}")
                    # Still keep the row if possible, just marking it for review
                    row.update({"category": "Other", "priority": "Low", "reason": f"Error during processing: {e}", "flag": "NEEDS_REVIEW"})
                    results.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Batch processing complete. Results written to {args.output}")
