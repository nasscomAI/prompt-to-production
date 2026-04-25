"""
UC-0A — Complaint Classifier
Implementation based on the RICE prompt (agents.md) and skills.md.
"""
import argparse
import csv
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify_complaint(row: dict) -> dict:
    """
    Analyzes a single dictionary representing a complaint row and returns 
    a classification object based on RICE enforcement rules.
    """
    desc = row.get('description', '')
    complaint_id = row.get('complaint_id', '')
    
    # Default fallback classification (from skills.md error handling)
    classification = {
        'complaint_id': complaint_id,
        'category': 'Other',
        'priority': 'Standard',
        'reason': '',
        'flag': ''
    }

    if not desc or len(desc.strip()) < 5:
        classification['flag'] = 'NEEDS_REVIEW'
        classification['reason'] = 'Description is missing or too short.'
        return classification

    desc_lower = desc.lower()

    # Rule 2: Priority enforcement
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_urgent = [kw for kw in urgent_keywords if kw in desc_lower]
    
    if found_urgent:
        classification['priority'] = 'Urgent'
    else:
        classification['priority'] = 'Standard'

    # Rule 1: Category matching
    category_mapping = {
        'Pothole': ['pothole', 'crater', 'hole'],
        'Flooding': ['flood', 'waterlog', 'submerge', 'overflow'],
        'Streetlight': ['streetlight', 'lamp', 'dark', 'light'],
        'Waste': ['waste', 'garbage', 'trash', 'rubbish', 'dump'],
        'Noise': ['noise', 'loud', 'music', 'sound', 'party'],
        'Road Damage': ['road damage', 'crack', 'broken road', 'uneven'],
        'Heritage Damage': ['heritage', 'monument', 'statue', 'historic'],
        'Heat Hazard': ['heat', 'hot', 'sun', 'temperature'],
        'Drain Blockage': ['drain', 'sewer', 'blockage', 'clogged']
    }

    matched_categories = []
    matched_words = []
    
    for cat, kws in category_mapping.items():
        for kw in kws:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_words.append(kw)

    # Rule 3 & 4: Reason citing and ambiguous flags
    if len(matched_categories) == 1:
        classification['category'] = matched_categories[0]
        
        # Construct reason citing specific words
        reason_text = f"Category keyword '{matched_words[0]}' found."
        if found_urgent:
            reason_text += f" Priority keyword '{found_urgent[0]}' found."
        classification['reason'] = reason_text

    elif len(matched_categories) > 1:
        classification['category'] = 'Other'
        classification['flag'] = 'NEEDS_REVIEW'
        classification['reason'] = f"Ambiguous: matched multiple categories ({', '.join(matched_categories)})."
        
    else:
        classification['category'] = 'Other'
        classification['flag'] = 'NEEDS_REVIEW'
        classification['reason'] = "No specific category keywords found in description."

    return classification


def batch_classify(input_path: str, output_path: str):
    """
    Reads a CSV file, iterates through rows, applies classify_complaint per row, 
    and writes the results to a new CSV.
    """
    if not os.path.exists(input_path):
        logging.error(f"Input file not found: {input_path}")
        return

    results = []
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']

    # Read and process input rows
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, start=1):
                if not row:
                    logging.warning(f"Row {row_num} is empty, skipping.")
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    logging.error(f"Failed to process row {row_num}: {e}")
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        return

    # Ensure output is written even if some rows failed
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"Successfully wrote {len(results)} rows to {output_path}")
    except Exception as e:
        logging.error(f"Error writing to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input test CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
