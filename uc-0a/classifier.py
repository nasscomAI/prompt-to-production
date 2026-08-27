"""
UC-0A — Complaint Classifier
Implemented using agents.md and skills.md.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get('description', '').strip()
    if not desc:
        return {
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Invalid input: missing or empty description',
            'flag': 'NEEDS_REVIEW'
        }
    
    desc_lower = desc.lower()
    
    # Severity keywords that trigger Urgent
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Urgent' if any(k in desc_lower for k in severity_keywords) else 'Standard'
    
    # Category mapping based on keywords in description
    category_map = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'streetlight': 'Streetlight',
        'waste': 'Waste',
        'noise': 'Noise',
        'road damage': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain': 'Drain Blockage'
    }
    
    category = 'Other'
    matched_keyword = None
    for key, cat in category_map.items():
        if key in desc_lower:
            category = cat
            matched_keyword = key
            break
    
    if category == 'Other':
        reason = f"The description '{desc}' does not clearly match any specific category."
        flag = 'NEEDS_REVIEW'
    else:
        reason = f"The description mentions '{matched_keyword}', which indicates {category}."
        flag = ''
    
    return {
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
        
        if not rows:
            raise ValueError("Input CSV is empty")
        
        classified_rows = []
        for row in rows:
            classification = classify_complaint(row)
            new_row = row.copy()
            new_row.update(classification)
            classified_rows.append(new_row)
        
        fieldnames = list(rows[0].keys()) + ['category', 'priority', 'reason', 'flag']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
        
        print(f"Successfully classified {len(classified_rows)} complaints.")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found")
    except Exception as e:
        raise RuntimeError(f"Error processing CSV: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
