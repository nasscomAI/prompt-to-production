"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration from RICE (agents.md)
CATEGORY_TAXONOMY = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "car damage", "tyre damage"],
    "Flooding": ["flood", "water", "inundated", "rain", "submerged"],
    "Streetlight": ["streetlight", "dark", "light", "electricity", "lamp"],
    "Waste": ["garbage", "trash", "waste", "dump", "smell", "animal"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road surface", "cracked", "pavement", "sinking"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "hot", "sun", "temperature"],
    "Drain Blockage": ["drain", "sewer", "gutter", "overflowing"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description.
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    reason_keyword = ""
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc:
                category = cat
                reason_keyword = kw
                break
        if category != "Other":
            break
            
    # 2. Determine Priority
    priority = "Standard"
    urgent_found = [kw for kw in URGENT_KEYWORDS if kw in desc]
    if urgent_found:
        priority = "Urgent"
        priority_reason = f"severity keywords found: {', '.join(urgent_found)}"
    else:
        priority_reason = "no urgent triggers found"

    # 3. Generate Reason (One sentence citing specific words)
    if category != "Other":
        reason = f"Classified as {category} because the description mentions '{reason_keyword}'. Priority is {priority} as {priority_reason}."
    else:
        reason = f"Category could not be definitively determined from description, defaulted to Other. Priority is {priority}."

    # 4. Set Flag
    flag = "NEEDS_REVIEW" if category == "Other" or not desc else ""

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
    
    print(f"Starting classification: {args.input} -> {args.output}")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
