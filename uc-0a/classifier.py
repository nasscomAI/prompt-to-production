"""
UC-0A — Complaint Classifier
Full implementation following agents.md RICE rules, skills.md specs, and README schema.
Processes input CSV (complaint_id, description) → output CSV (category, priority, reason, flag).
Enforces exact categories, Urgent keywords, citations, ambiguity handling.
"""
import argparse
import csv
import re
import os

# Exact categories from README
CATEGORIES = {
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
}

# Urgent keywords (case-insensitive)
URGENT_KEYWORDS = {
    'injury', 'child', 'school', 'hospital', 'ambulance', 
    'fire', 'hazard', 'fell', 'collapse'
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row per RICE enforcement.
    Input: {'complaint_id': str, 'description': str}
    Output: {'category': str, 'priority': str, 'reason': str, 'flag': str}
    """
    description = (row.get('description', '') or '').strip().lower()
    
    if not description:
        return {
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'Invalid or empty description.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Check for Urgent
    is_urgent = any(re.search(r'\b' + re.escape(kw) + r'\b', description, re.IGNORECASE) for kw in URGENT_KEYWORDS)
    priority = 'Urgent' if is_urgent else 'Standard'
    
    # Category matching (keyword-based, strict to list)
    category_matches = {
        'Pothole': ['pothole', 'crater', 'road hole', 'pot hole', 'hole in road'],
'Flooding': ['flood', 'waterlogging', 'flooding'],
        'Streetlight': ['streetlight', 'street light', 'light not working', 'light', 'lamp'],
        'Waste': ['garbage', 'waste', 'trash', 'rubbish'],
        'Noise': ['noise', 'loud', 'loud music', 'barking', 'sound'],
        'Road Damage': ['road damage', 'broken road', 'cracks', 'crack'],
        'Heritage Damage': ['heritage', 'monument', 'monument damage'],
        'Heat Hazard': ['heat', 'sunstroke', 'hot road', 'melting'],
        'Drain Blockage': ['drain', 'sewage', 'sewer', 'blockage', 'clogged']
    }
    
    matched_keys = []
    for cat, keywords in category_matches.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', description, re.IGNORECASE) for kw in keywords):
            matched_keys.append(cat)
    
    flag = ''
    if len(matched_keys) == 1:
        category = matched_keys[0]
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    
    # Reason always cites words
    all_keywords = [kw for kw_list in category_matches.values() for kw in kw_list] + list(URGENT_KEYWORDS)
    cited_words_list = re.findall(r'\b(?:' + '|'.join(re.escape(kw) for kw in all_keywords) + r')\b', description, re.IGNORECASE)
    cited_words = ', '.join(cited_words_list[:3])
    urgent_words = [kw for kw in URGENT_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', description, re.IGNORECASE)]
    urgency_note = f", urgent: {', '.join(urgent_words[:2])}" if urgent_words else ''
    reason = f"Detected keywords: {cited_words}{urgency_note}" if cited_words else "No clear matching keywords found in description"
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Batch process CSV per skills.md.
    Handles errors per row, writes output always.
    """
    results = []
    errors = []
    
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return
    
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, 1):
                try:
                    clean_row = {'complaint_id': row.get('complaint_id', f'Row{row_num}'), 'description': row.get('description', '')}
                    result = classify_complaint(clean_row)
                    results.append(result)
                except Exception as e:
                    errors.append(f"Row {row_num}: {e}")
                    results.append({
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Processing error: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
        
        fieldnames = ['category', 'priority', 'reason', 'flag']
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Processed {len(results)} rows. Output: {output_path}")
        if errors:
            print("Errors:", errors)
            
    except Exception as e:
        print(f"Batch error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
