import argparse
import csv
import re

CATEGORY_KEYWORDS = {
    'Pothole': ['pothole'],
    'Flooding': ['flood', 'flooded', 'water'],
    'Streetlight': ['streetlight', 'lamp'],
    'Waste': ['waste', 'garbage', 'trash', 'dump'],
    'Noise': ['noise', 'loud'],
    'Road Damage': ['road', 'crack', 'asphalt'],
    'Heritage Damage': ['heritage', 'monument', 'historical'],
    'Heat Hazard': ['heat', 'temperature', 'sunstroke'],
    'Drain Blockage': ['drain', 'blocked', 'clog', 'sewer']
}

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(description):
    if not description or not isinstance(description, str):
        return 'Other', 'Standard', 'No description provided.', 'NEEDS_REVIEW'

    desc_lower = description.lower()
    
    matched_categories = []
    reason_words = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                if cat not in matched_categories:
                    matched_categories.append(cat)
                reason_words.append(kw)
    
    if not matched_categories:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = 'NEEDS_REVIEW'
    else:
        category = matched_categories[0]
        flag = ''
        
    priority = 'Standard'
    severity_words_found = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            priority = 'Urgent'
            severity_words_found.append(kw)
            
    if severity_words_found:
        reason = f"Severity keyword(s) '{', '.join(severity_words_found)}' found. "
    else:
        reason = ""
        
    if reason_words:
        reason += f"Matched category keyword(s): '{', '.join(reason_words)}'."
    else:
        reason += "No specific category keywords found."
        
    return category, priority, reason.strip(), flag

def batch_classify(input_csv, output_csv):
    try:
        with open(input_csv, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if 'description' not in fieldnames:
                print("Error: Input CSV must contain a 'description' column.")
                return
            
            out_fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            
            with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    desc = row.get('description', '')
                    cat, prio, res, flg = classify_complaint(desc)
                    writer.writerow({
                        'complaint_id': row.get('complaint_id', ''),
                        'category': cat,
                        'priority': prio,
                        'reason': res,
                        'flag': flg
                    })
        print(f"Successfully processed {input_csv} and saved results to {output_csv}")
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Classify citizen complaints.')
    parser.add_argument('--input', required=True, help='Path to input CSV')
    parser.add_argument('--output', required=True, help='Path to output CSV')
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
