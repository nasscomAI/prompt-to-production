import argparse
import csv
import os

# Configuration based on agents.md
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'
]

# Simple mapping logic to simulate agent's intelligence while following rigid rules
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit"],
    "Flooding": ["flood", "waterlogging", "rain water", "water logging"],
    "Streetlight": ["streetlight", "light", "lamp", "dark"],
    "Waste": ["garbage", "trash", "waste", "dump", "litter"],
    "Noise": ["noise", "loud", "sound", "music", "horn"],
    "Road Damage": ["road", "pavement", "broken road"],
    "Heritage Damage": ["heritage", "statue", "monument", "historic"],
    "Heat Hazard": ["heat", "hot", "sunstroke", "dehydration"],
    "Drain Blockage": ["drain", "sewage", "gutter", "block", "choke"]
}

def classify_complaint(description: str) -> dict:
    """
    Classifies a raw complaint description.
    Following the agents.md 'Rigid Compliance-First' protocol.
    """
    desc_lower = description.lower()
    
    # 1. Determine Category (Zero-Tolerance for Taxonomy Drift)
    assigned_category = "Other"
    found_keyword = None
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                assigned_category = category
                found_keyword = kw
                break
        if assigned_category != "Other":
            break
            
    # 2. Determine Priority (Deterministic Escalation)
    priority = "Standard"
    urgent_found = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if urgent_found:
        priority = "Urgent"
        found_keyword = urgent_found[0] # Prioritize urgent keyword for citation if found
    elif "low" in desc_lower or "minor" in desc_lower:
        priority = "Low"

    # 3. Handle Ambiguity/Refusal (Ambiguity Protocol)
    flag = ""
    if assigned_category == "Other" or len(description.split()) < 3:
        flag = "NEEDS_REVIEW"
        assigned_category = "Other"

    # 4. Generate Reason (Citation Protocol)
    # Must be one sentence citing specific words.
    if found_keyword:
        reason = f"Classified because the description contained the specific term '{found_keyword}'."
    elif flag == "NEEDS_REVIEW":
        reason = "The description is too ambiguous or short to classify reliably."
    else:
        reason = "Classified as Standard based on general infrastructure impact."

    return {
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, applies classification, and writes results.
    Refines rows as per skills.md specifications.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    fieldnames = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            for row in reader:
                description = row.get('description', '')
                classification = classify_complaint(description)
                
                # Merge original row data with classification
                row.update(classification)
                results.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
