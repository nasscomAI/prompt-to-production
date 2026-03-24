import argparse
import csv
import sys
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with updated keys: category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Priority rules
    priority = 'Standard'
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    for kw in severity_keywords:
        if kw in desc:
            priority = 'Urgent'
            break
            
    # Category rules
    category_map = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'drain': 'Drain Blockage',
        'streetlight': 'Streetlight',
        'lights out': 'Streetlight',
        'sparking': 'Streetlight',
        'garbage': 'Waste',
        'dead animal': 'Waste',
        'waste': 'Waste',
        'smell': 'Waste',
        'music': 'Noise',
        'crack': 'Road Damage',
        'sinking': 'Road Damage',
        'broken': 'Road Damage',
        'manhole': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
    }
    
    category = 'Other'
    flag = 'NEEDS_REVIEW'
    reason = 'No clear category matched in the description.'
    
    for word, cat in category_map.items():
        if word in desc:
            category = cat
            flag = ''
            reason = f"Complaint specifies '{word}'."
            break

    # Construct result ensuring all original keys are preserved, adding the new ones
    result = row.copy()
    result['category'] = category
    result['priority'] = priority
    result['reason'] = reason
    result['flag'] = flag
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            # Add new fields if they don't exist
            fieldnames = reader.fieldnames
            for f in ['category', 'priority', 'reason', 'flag']:
                if f not in fieldnames:
                    fieldnames.append(f)
            
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for index, row in enumerate(rows):
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    print(f"Error processing row {index + 1}: {e}")
                    
    except Exception as e:
        print(f"Error reading or writing files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(base_dir, '..', 'data', 'city-test-files', 'test_hyderabad.csv')
    default_output = os.path.join(base_dir, 'results_hyderabad.csv')

    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", default=default_input, help="Path to test_[city].csv")
    parser.add_argument("--output", default=default_output, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
