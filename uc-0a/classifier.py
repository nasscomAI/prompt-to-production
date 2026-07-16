"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

CATEGORIES_KEYWORDS = {
    'Pothole': ['pothole'],
    'Flooding': ['flood', 'waterlog', 'rainwater', 'rain '],
    'Streetlight': ['streetlight', 'lamp post', 'unlit', 'lights out', 'darkness'],
    'Waste': ['waste', 'garbage', 'bin', 'dump', 'dead animal', 'litter', 'trash'],
    'Noise': ['noise', 'music', 'loud', 'audible', 'sound', 'amplifier', 'playing', 'idling', 'drilling'],
    'Heritage Damage': ['heritage', 'ancient', 'monument', 'historic', 'museum'],
    'Heat Hazard': ['heat', 'temperature', 'melt', '44°c', '45°c', '52°c', 'heatwave', 'burn', 'full sun', 'sun '],
    'Drain Blockage': ['drain', 'sewer', 'manhole', 'block'],
    'Road Damage': ['road surface', 'crack', 'sink', 'subsidence', 'paving', 'footpath', 'tile', 'pavement', 'road collapsed', 'surface buckled', 'road subsided', 'tarmac surface', 'cobblestones', 'broken up']
}

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    if not description:
        return {
            'complaint_id': row.get('complaint_id', ''),
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW'
        }
    
    desc_lower = description.lower()
    
    # Identify matching categories
    matched_cats = {}
    for cat, keywords in CATEGORIES_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in desc_lower]
        if matches:
            matched_cats[cat] = matches
            
    # Determine priority
    severity_matched = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = 'Urgent' if severity_matched else 'Standard'
    
    flag = ''
    category = 'Other'
    reason_parts = []
    
    if not matched_cats:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        reason_parts.append("no matching category keywords found in description")
    elif len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        keywords_cited = ", ".join(matched_cats[category])
        reason_parts.append(f"description mentions '{keywords_cited}'")
    else:
        # Multiple matching categories - pick the one with most matches, or first in alphabetical order
        sorted_cats = sorted(matched_cats.items(), key=lambda item: (-len(item[1]), item[0]))
        category = sorted_cats[0][0]
        flag = 'NEEDS_REVIEW'
        keywords_cited = ", ".join(matched_cats[category])
        other_cats = ", ".join([c for c, _ in sorted_cats[1:]])
        reason_parts.append(f"description mentions '{keywords_cited}' but also matches other categories ({other_cats})")
        
    if priority == 'Urgent':
        severity_cited = ", ".join(severity_matched)
        reason_parts.append(f"priority set to Urgent due to severity keyword(s): '{severity_cited}'")
        
    # Join into a single sentence reason
    reason = f"Classified as {category} because " + " and ".join(reason_parts) + "."
    
    return {
        'complaint_id': row.get('complaint_id', ''),
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
        raise FileNotFoundError(f"Input file not found at {input_path}")
        
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("Input CSV file is empty or has no header.")
            
        for row in reader:
            try:
                # Classify the row
                classification = classify_complaint(row)
                # Combine original row content with classification fields
                # Ensure we have all columns from original, plus the new classification fields
                out_row = dict(row)
                out_row.update(classification)
                results.append(out_row)
            except Exception as e:
                # Log or handle parsing error for individual rows
                print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
                
    # Prepare output fields: original columns + classification columns (if not already present)
    # The requirement is that results should have category, priority, reason, flag
    out_headers = list(fieldnames)
    for extra in ['category', 'priority', 'reason', 'flag']:
        if extra not in out_headers:
            out_headers.append(extra)
            
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_headers)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
