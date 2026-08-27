"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

# Severity keywords from README/agents.md
SEVERITY_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'
]

# Allowed categories from README/agents.md
ALLOWED_CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 
    'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic to simulate the agent's behavior.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').strip()
    desc_lower = description.lower()
    
    # 1. Determine Category (Taxonomy Match)
    category = "Other"
    reason_word = ""
    
    category_map = {
        'Pothole': ['pothole', 'crater', 'hole in road'],
        'Flooding': ['flood', 'water logging', 'waterlogged', 'submerged', 'inundation'],
        'Streetlight': ['streetlight', 'street light', 'lamp', 'dark', 'light out', 'flickering'],
        'Waste': ['garbage', 'trash', 'waste', 'litter', 'dump', 'smell', 'bins', 'dead animal'],
        'Noise': ['noise', 'loud', 'music', 'sound', 'volume', 'midnight'],
        'Road Damage': ['road surface', 'cracked', 'sinking', 'footpath', 'tiles', 'uneven'],
        'Heritage Damage': ['heritage', 'monument', 'historical', 'old city'],
        'Heat Hazard': ['heat', 'cooling', 'dehydration', 'sunstroke'],
        'Drain Blockage': ['drain', 'sewage', 'overflow', 'blocked', 'gutter', 'manhole']
    }
    
    # Simple keyword search for category
    found_categories = []
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc_lower:
                found_categories.append((cat, kw))
                break
                
    if found_categories:
        # If multiple, take the first one found (simplification)
        category, reason_word = found_categories[0]
    
    # 2. Determine Priority (Severity Blindness Prevention)
    priority = "Standard"
    severity_trigger = ""
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            severity_trigger = kw
            break
            
    # 3. Handle Ambiguity (NEEDS_REVIEW flag)
    flag = ""
    if len(found_categories) > 1 or not found_categories:
        flag = "NEEDS_REVIEW"
        if not found_categories:
            category = "Other"
    
    # 4. Generate Reason (Citation Enforcement)
    if severity_trigger:
        reason = f"Classified as {category} with Urgent priority due to the mention of '{severity_trigger}'."
    elif reason_word:
        reason = f"Identified as {category} based on the description of '{reason_word}'."
    else:
        reason = "Classified as Other due to lack of specific category keywords in the description."

    return {
        'complaint_id': row.get('complaint_id', 'Unknown'),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    # Merge classification results into the row
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    # Ensure we don't crash the whole batch
                    continue
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Critical error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
