"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Category keywords mapping
CATEGORY_KEYWORDS = {
    'Pothole': ['pothole', 'hole', 'crater', 'dip', 'depression'],
    'Flooding': ['flood', 'water', 'rain', 'overflow', 'submerged'],
    'Streetlight': ['streetlight', 'light', 'lamp', 'bulb', 'dark'],
    'Waste': ['waste', 'garbage', 'trash', 'dump', 'litter'],
    'Noise': ['noise', 'loud', 'sound', 'music', 'party'],
    'Road Damage': ['road', 'damage', 'crack', 'broken', 'repair'],
    'Heritage Damage': ['heritage', 'historical', 'monument', 'damage', 'vandalism'],
    'Heat Hazard': ['heat', 'hot', 'temperature', 'sun', 'burn'],
    'Drain Blockage': ['drain', 'block', 'clog', 'sewage', 'pipe'],
    'Other': []  # Default if no match
}

# Severity keywords that trigger Urgent priority
URGENT_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').lower()
    
    # Determine category
    category = 'Other'
    matched_words = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if cat == 'Other':
            continue
        for keyword in keywords:
            if keyword in description:
                category = cat
                matched_words.append(keyword)
                break
        if category != 'Other':
            break
    
    # Determine priority
    priority = 'Low'
    urgent_triggered = any(keyword in description for keyword in URGENT_KEYWORDS)
    if urgent_triggered:
        priority = 'Urgent'
    elif category != 'Other':
        priority = 'Standard'
    
    # Generate reason
    if matched_words:
        reason = f"The complaint mentions '{matched_words[0]}' which indicates {category.lower()}."
    else:
        reason = "The complaint description does not clearly match any specific category."
    
    # Determine flag
    flag = ''
    if category == 'Other' or len(matched_words) == 0:
        flag = 'NEEDS_REVIEW'
    
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
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
        
        classified_rows = []
        for row in rows:
            try:
                classified = classify_complaint(row)
                # Combine original row with classification
                combined = {**row, **classified}
                classified_rows.append(combined)
            except Exception as e:
                # On failure, mark as Other with NEEDS_REVIEW
                combined = {**row, 
                           'category': 'Other', 
                           'priority': 'Low', 
                           'reason': f'Classification failed: {str(e)}', 
                           'flag': 'NEEDS_REVIEW'}
                classified_rows.append(combined)
        
        if classified_rows:
            fieldnames = list(classified_rows[0].keys())
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(classified_rows)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found")
    except Exception as e:
        raise Exception(f"Error processing files: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
