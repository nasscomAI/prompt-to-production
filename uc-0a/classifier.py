import csv
import argparse
import os

# 1. Define the strict schema from your instructions
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    """Logic to satisfy UC-0A Enforcement Rules"""
    desc_lower = description.lower()
    
    # Default values
    category = "Other"
    priority = "Standard"
    reason = "General maintenance request."
    flag = ""

    # Rule: Category Mapping (Simplified keyword matching for the demo)
    if "pothole" in desc_lower: category = "Pothole"
    elif "flood" in desc_lower or "water" in desc_lower: category = "Flooding"
    elif "light" in desc_lower: category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower: category = "Waste"
    elif "noise" in desc_lower: category = "Noise"
    elif "road" in desc_lower: category = "Road Damage"
    elif "heritage" in desc_lower: category = "Heritage Damage"
    elif "heat" in desc_lower: category = "Heat Hazard"
    elif "drain" in desc_lower: category = "Drain Blockage"

    # Rule: Severity/Priority Enforcement
    found_keywords = [word for word in SEVERITY_KEYWORDS if word in desc_lower]
    if found_keywords:
        priority = "Urgent"
        reason = f"Urgent because '{found_keywords[0]}' was mentioned in description."
    else:
        reason = f"Classified as {category} based on description keywords."

    # Rule: Ambiguity Flag
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag

def batch_classify(input_file, output_file):
    """Reads input, processes rows, and writes to output CSV"""
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    results = []
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get the description (ensure column name matches your CSV)
            desc = row.get('description', '')
            
            cat, prio, reas, flg = classify_complaint(desc)
            
            # Update the row with new fields
            row['category'] = cat
            row['priority'] = prio
            row['reason'] = reas
            row['flag'] = flg
            results.append(row)

    # Write to the output file
    if results:
        keys = results[0].keys()
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success! Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
