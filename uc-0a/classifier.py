"""
UC-0A — Complaint Classifier
Implementation heavily based on the RICE -> agents.md enforcement rules.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on text content rules from agents.md.
    Returns: dict with new keys: category, priority, reason, flag
    """
    description = row.get('description', '')
    desc_lower = description.lower()
    
    # Priority Rule: Urgent if specific keywords present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severe = [kw for kw in severity_keywords if kw in desc_lower]
    priority = 'Urgent' if found_severe else 'Standard'
    
    # Category Assignment Rules
    category = 'Other'
    if 'pothole' in desc_lower:
        category = 'Pothole'
    elif 'flood' in desc_lower:
        category = 'Flooding'
    elif 'streetlights' in desc_lower or 'streetlight' in desc_lower or 'lights out' in desc_lower:
        category = 'Streetlight'
    elif 'garbage' in desc_lower or 'waste' in desc_lower or 'dead animal' in desc_lower:
        category = 'Waste'
    elif 'music' in desc_lower or 'noise' in desc_lower:
        category = 'Noise'
    elif 'cracked and sinking' in desc_lower or 'tiles broken' in desc_lower:
        category = 'Road Damage'
    elif 'heritage' in desc_lower and 'damage' in desc_lower:
        category = 'Heritage Damage'
    elif 'heat' in desc_lower:
        category = 'Heat Hazard'
    elif 'drain' in desc_lower and 'blocked' in desc_lower:
        category = 'Drain Blockage'
        
    # Flag rule: NEEDS_REVIEW if ambiguous
    flag = 'NEEDS_REVIEW' if category == 'Other' else ''
    
    # Reason formulation citing specific words
    if found_severe:
        reason = f"Classified as Urgent due to presence of severity keywords: {', '.join(found_severe)}."
    elif category != 'Other':
        reason = f"Classified as {category} based on description context."
    else:
        reason = "Category ambiguous, flagged for manual review."
        
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, ignores bad rows to ensure output is written.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            
            for row in reader:
                if not row.get('description'):
                    row['category'] = 'Other'
                    row['priority'] = 'Low'
                    row['reason'] = 'No description provided.'
                    row['flag'] = 'NEEDS_REVIEW'
                else:    
                    try:
                        classification = classify_complaint(row)
                        row.update(classification)
                    except Exception as e:
                        print(f"Failed to process row {row.get('complaint_id', 'unknown')}: {e}")
                        continue # Skip to next row
                results.append(row)
                
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
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
    print(f"Done. Processed results written to {args.output}")
