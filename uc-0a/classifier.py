"""
UC-0A — Complaint Classifier
Built using agents.md and skills.md.
"""
import argparse
import csv

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
ALLOWED_CATEGORIES = ['Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other']

def classify_category(description: str) -> str:
    """
    Classify the category based on keywords in description.
    """
    desc_lower = description.lower()
    if 'pothole' in desc_lower or 'hole' in desc_lower and 'road' in desc_lower:
        return 'Pothole'
    elif 'flood' in desc_lower or 'water' in desc_lower and 'street' in desc_lower:
        return 'Flooding'
    elif 'streetlight' in desc_lower or 'light' in desc_lower and 'out' in desc_lower:
        return 'Streetlight'
    elif 'waste' in desc_lower or 'garbage' in desc_lower:
        return 'Waste'
    elif 'noise' in desc_lower:
        return 'Noise'
    elif 'road damage' in desc_lower or 'damage' in desc_lower and 'road' in desc_lower:
        return 'Road Damage'
    elif 'heritage' in desc_lower or 'historical' in desc_lower:
        return 'Heritage Damage'
    elif 'heat' in desc_lower or 'hot' in desc_lower and 'hazard' in desc_lower:
        return 'Heat Hazard'
    elif 'drain' in desc_lower or 'blockage' in desc_lower:
        return 'Drain Blockage'
    else:
        return 'Other'

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    category = classify_category(description)
    priority = 'Urgent' if any(kw in description.lower() for kw in SEVERITY_KEYWORDS) else 'Standard'
    # Reason: one sentence citing specific words
    cited_words = [kw for kw in description.split() if kw.lower() in [cat.lower() for cat in ALLOWED_CATEGORIES] or kw.lower() in SEVERITY_KEYWORDS]
    reason = f"The complaint mentions '{', '.join(cited_words) if cited_words else 'general issues'}' indicating {category.lower()}."
    flag = 'NEEDS_REVIEW' if category == 'Other' else ''
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
    try:
        with open(input_path, 'r') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found.")
    
    results = []
    for row in rows:
        try:
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            # For bad rows, add with Other and flag
            results.append({
                'complaint_id': row.get('complaint_id', ''),
                'category': 'Other',
                'priority': 'Standard',
                'reason': f"Error processing row: {str(e)}",
                'flag': 'NEEDS_REVIEW'
            })
    
    try:
        with open(output_path, 'w', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        raise ValueError(f"Error writing to output file {output_path}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
