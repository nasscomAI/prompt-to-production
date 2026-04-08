"""
UC-0A — Complaint Classifier
Implemented using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using heuristic keyword matching.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', 'Unknown')
    
    # Predefined Taxonomy
    categories = {
        'Pothole': ['pothole', 'pot hole', 'hole in road'],
        'Flooding': ['flooded', 'flooding', 'flood', 'waterlogging', 'water log', 'rain water', 'submerged'],
        'Streetlight': ['streetlight', 'street light', 'lamp', 'dark', 'light out'],
        'Waste': ['garbage', 'waste', 'trash', 'smell', 'dumped', 'bins', 'dead animal'],
        'Noise': ['noise', 'music', 'loud', 'midnight', 'sound'],
        'Road Damage': ['road surface', 'cracked', 'sinking', 'footpath', 'tiles broken', 'manhole'],
        'Heritage Damage': ['heritage'],
        'Heat Hazard': ['heat', 'hot', 'sun'],
        'Drain Blockage': ['drain', 'blocked', 'overflowing drain'],
    }
    
    # Priority Keywords
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    # Detect Category
    detected_categories = []
    for cat, keywords in categories.items():
        if any(kw in description for kw in keywords):
            detected_categories.append(cat)
    
    # Determine Category and Flag
    category = 'Other'
    flag = ''
    if len(detected_categories) == 1:
        category = detected_categories[0]
    elif len(detected_categories) > 1:
        # If multiple matches, pick the first but flag for review
        category = detected_categories[0]
        flag = 'NEEDS_REVIEW'
    else:
        # No clear match
        category = 'Other'
        flag = 'NEEDS_REVIEW'

    # Special case for "Heritage" which often co-occurs with lights or roads in the test data
    if 'heritage' in description:
        category = 'Heritage Damage'
        flag = ''

    # Detect Priority
    priority = 'Standard'
    found_urgent_kw = [kw for kw in urgent_keywords if kw in description]
    if found_urgent_kw:
        priority = 'Urgent'
    elif 'smell' in description or 'midnight' in description:
        priority = 'Low'
        
    # Generate Reason citing specific words
    cited_words = []
    # Use the detected category keywords or priority keywords for citation
    all_keywords = []
    if category in categories:
        all_keywords.extend(categories[category])
    all_keywords.extend(found_urgent_kw)
    
    for kw in all_keywords:
        if kw in description:
            cited_words.append(kw)
    
    # Limit to unique cited words
    cited_words = list(set(cited_words))
    cited_str = ", ".join(cited_words) if cited_words else "nature of the issue"
    
    reason = f"Classified as {category} with {priority} priority because the description mentions '{cited_str}'."
    
    return {
        'complaint_id': complaint_id,
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Basic validation: flag nulls
                if not row.get('description'):
                    results.append({
                        'complaint_id': row.get('complaint_id', 'Unknown'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Missing description in input.',
                        'flag': 'NEEDS_REVIEW'
                    })
                    continue
                
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    results.append({
                        'complaint_id': row.get('complaint_id', 'Unknown'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Error during classification: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })

        # Write results
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
