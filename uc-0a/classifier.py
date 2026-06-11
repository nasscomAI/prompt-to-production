import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get('description', '').lower()
    
    # Priority check
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(word in desc for word in urgent_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Category mapping
    category = "Other"
    if "pothole" in desc or "crater" in desc: category = "Pothole"
    elif "flood" in desc or "waterlogging" in desc: category = "Flooding"
    elif "light" in desc: category = "Streetlight"
    elif "waste" in desc or "garbage" in desc: category = "Waste"
    elif "noise" in desc or "loud" in desc: category = "Noise"
    elif "road damage" in desc: category = "Road Damage"
    elif "heritage" in desc: category = "Heritage Damage"
    elif "heat" in desc: category = "Heat Hazard"
    elif "drain" in desc: category = "Drain Blockage"
    
    # Needs review if it's very ambiguous or "Other"
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # Reason citing
    reason = "No description provided."
    if desc:
        reason = f"Mentioned '{desc.split()[0]}...' in description."
        for w in urgent_keywords:
            if w in desc:
                reason = f"Found urgent keyword '{w}'."
                break
    
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            results.append({
                'complaint_id': row.get('complaint_id', ''),
                'category': 'Other',
                'priority': 'Standard',
                'reason': f"Error: {str(e)}",
                'flag': 'NEEDS_REVIEW'
            })
            
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
