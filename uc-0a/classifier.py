"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

# Allowed Categories
CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

# Severity Keywords
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

# Category mapping keywords
CATEGORY_MAPPING = {
    'Pothole': ['pothole'],
    'Flooding': ['flood', 'rain', 'water'],
    'Streetlight': ['streetlight', 'dark', 'unlit', 'light'],
    'Waste': ['waste', 'garbage', 'dead animal', 'bin', 'dump'],
    'Noise': ['noise', 'music', 'club', 'loud'],
    'Road Damage': ['road surface', 'subsidence', 'cracked', 'tiles broken', 'tarmac'],
    'Heritage Damage': ['heritage', 'ancient'],
    'Heat Hazard': ['heatwave', 'burn', 'melting', '44°c', '45°c', '52°c', 'sun', 'temperatures'],
    'Drain Blockage': ['drain block', 'drain blocked']
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "No specific match."
    flag = "NEEDS_REVIEW"
    
    # 1. Determine priority
    found_sc = []
    for sc in SEVERITY_KEYWORDS:
        if sc in desc:
            found_sc.append(sc)
            priority = "Urgent"
            
    # 2. Determine category
    found_cc = None
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in desc:
                category = cat
                found_cc = kw
                flag = ""
                break
        if found_cc:
            break
            
    # Priority defaults to Low if no urgent keywords and no clear category
    if priority == "Standard" and category == "Other":
        priority = "Low"

    # 3. Form reason
    if category != "Other":
        if found_sc:
            reason = f"Description contains category keyword '{found_cc}' and severity keyword '{found_sc[0]}'."
        else:
            reason = f"Description contains category keyword '{found_cc}'."
    else:
        if found_sc:
            reason = f"Description contains severity keyword '{found_sc[0]}' but no clear category."
        else:
            reason = "Category could not be definitively determined from description."

    
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
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            print("Empty or invalid CSV file.")
            sys.exit(1)
            
        output_fieldnames = fieldnames + ['category', 'priority', 'reason', 'flag']
        
        results = []
        for row in reader:
            try:
                classification = classify_complaint(row)
                row['category'] = classification['category']
                row['priority'] = classification['priority']
                row['reason'] = classification['reason']
                row['flag'] = classification['flag']
            except Exception as e:
                # Must not crash on malformed rows
                row['category'] = "Other"
                row['priority'] = "Low"
                row['reason'] = f"Error processing row: {e}"
                row['flag'] = "NEEDS_REVIEW"
                
            results.append(row)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
