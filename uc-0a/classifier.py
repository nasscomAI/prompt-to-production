"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").strip()
    
    # 1. Enforcement: If description is missing, set flag: NEEDS_REVIEW and category: Other.
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is missing from the input.",
            "flag": "NEEDS_REVIEW"
        }
    
    # 2. Enforcement: Priority must be [Urgent, Standard, Low]. Urgent if severity keywords are present.
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_severity_word = None
    for kw in severity_keywords:
        if kw.lower() in description.lower():
            priority = "Urgent"
            found_severity_word = kw
            break
            
    # 3. Enforcement: Category must be exactly one of the allowed list.
    category_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "water", "overflow"],
        "Streetlight": ["streetlight", "lamp", "light"],
        "Waste": ["garbage", "trash", "waste", "litter"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["crack", "road", "pavement"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "sun", "hot"],
        "Drain Blockage": ["drain", "sewage", "clogged"]
    }
    
    category = "Other"
    found_category_word = None
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw.lower() in description.lower():
                category = cat
                found_category_word = kw
                break
        if category != "Other":
            break
            
    # 4. Enforcement: Reason field citing specific words from the description.
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "The description does not clearly match a specific category."
    else:
        reason = f"Identified as {category} due to the presence of the word '{found_category_word}'."
        
    if priority == "Urgent":
        reason += f" Priority set to Urgent due to keyword '{found_severity_word}'."

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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                 print(f"Error: Input file {input_path} is empty or has no headers.")
                 return
                 
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    classification = classify_complaint(row)
                    row.update(classification)
                    writer.writerow(row)
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
