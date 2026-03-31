"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', 'UNKNOWN')
    
    # Priority logic
    urgent_keywords = ['risk', 'injury', 'hazard', 'child', 'school', 'fell', 'health', 'midnight', 'sparking', 'electrical']
    priority = "Urgent" if any(kw in description for kw in urgent_keywords) else "Normal"
    
    # Category logic
    categories = {
        'Pothole': ['pothole', 'hole in road'],
        'Flooding': ['flood', 'water logging', 'rain water', 'flooded'],
        'Streetlight': ['light', 'dark', 'bulb', 'flicker'],
        'Garbage': ['garbage', 'waste', 'dump', 'smell', 'animal'],
        'Noise': ['noise', 'music', 'loud'],
        'Sewage': ['sewage', 'drain', 'manhole'],
        'Road': ['road surface', 'crack', 'sink'],
        'Footpath': ['footpath', 'tiles', 'broken pavement']
    }
    
    category = "Other"
    reason = "No matching keywords found."
    for cat, kws in categories.items():
        for kw in kws:
            if kw in description:
                category = cat
                reason = f"Description contains matching keyword: '{kw}'"
                break
        if category != "Other":
            break
            
    # Flag logic
    flag = "VALID"
    if not description or description == 'null':
        flag = "NULL_DATA"
        category = "Other"
        reason = "Empty description."
    elif len(description.split()) < 5:
        flag = "NEEDS_REVIEW"
        reason = "Description too short."
        
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    import os
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                print(f"Error classifying row {row}: {e}")
                
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
