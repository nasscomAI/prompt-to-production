import argparse
import csv

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

def map_category(desc):
    desc_lower = desc.lower()
    if 'pothole' in desc_lower: return 'Pothole'
    if 'flood' in desc_lower: return 'Flooding'
    if 'heritage' in desc_lower: return 'Heritage Damage'
    if 'streetlight' in desc_lower or 'lights out' in desc_lower: return 'Streetlight'
    if 'waste' in desc_lower or 'garbage' in desc_lower or 'dead animal' in desc_lower: return 'Waste'
    if 'music' in desc_lower or 'noise' in desc_lower: return 'Noise'
    if 'road surface cracked' in desc_lower or 'footpath tiles' in desc_lower: return 'Road Damage'
    if 'manhole' in desc_lower or 'drain block' in desc_lower: return 'Drain Blockage'
    if 'heat' in desc_lower: return 'Heat Hazard'
    return 'Other'

def classify_complaint(row: dict) -> dict:
    desc = row.get('description', '')
    desc_lower = desc.lower()
    
    urgent = False
    found_keywords = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            urgent = True
            found_keywords.append(kw)
    
    priority = 'Urgent' if urgent else 'Standard'
    category = map_category(desc)
    
    if found_keywords:
        reason = f"Classified with priority because description explicitly mentions '{found_keywords[0]}'."
    else:
        cited_word = desc.split()[0] if desc else 'none'
        reason = f"Classified without urgent priority, citing word '{cited_word}'."
        
    flag = ''
    if category == 'Other':
        flag = 'NEEDS_REVIEW'
        
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f"Error parsing: {e}",
                        'flag': 'NEEDS_REVIEW'
                    })
    except Exception as e:
        print(f"Failed to read input: {e}")
        return

    if not results:
        print("No results to write.")
        return
        
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['complaint_id', 'category', 'priority', 'reason', 'flag'])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
