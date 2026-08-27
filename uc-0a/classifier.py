import csv
import argparse
import os

# Classification Taxonomy
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity Keywords
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    desc_lower = description.lower()
    
    # 1. Determine Category (Logic based on keywords)
    category = "Other"
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "rainwater" in desc_lower:
        category = "Flooding"
    elif "drain" in desc_lower:
        category = "Drain Blockage"
    elif "waste" in desc_lower or "garbage" in desc_lower:
        category = "Waste"
    elif "noise" in desc_lower or "drilling" in desc_lower or "trucks idling" in desc_lower:
        category = "Noise"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "collapse" in desc_lower or "crater" in desc_lower:
        category = "Road Damage"
    elif "streetlight" in desc_lower:
        category = "Streetlight"
    elif "heat" in desc_lower:
        category = "Heat Hazard"

    # 2. Determine Priority
    priority = "Low"
    found_severity = [word for word in SEVERITY_KEYWORDS if word in desc_lower]
    if found_severity:
        priority = "Urgent"
    elif any(word in desc_lower for word in ["risk", "concern", "unusable", "blocked"]):
        priority = "Standard"
        
    # 3. Generate Reason
    if found_severity:
        reason = f"Classified as {category} and set to Urgent because keywords '{', '.join(found_severity)}' were identified."
    else:
        reason = f"Classified as {category} based on description matching city service taxonomy."

    # 4. Flagging logic
    flag = ""
    if category == "Other" or ("flood" in desc_lower and "drain" in desc_lower):
        flag = "NEEDS_REVIEW"
        
    return category, priority, reason, flag

def batch_classify(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    results = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category, priority, reason, flag = classify_complaint(row['description'])
            row['category'] = category
            row['priority'] = priority
            row['reason'] = reason
            row['flag'] = flag
            results.append(row)

    if results:
        fieldnames = list(results[0].keys())
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} rows. Output saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify citizen complaints.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
