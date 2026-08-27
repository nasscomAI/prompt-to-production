import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    desc = row.get('description', '')
    desc_lower = desc.lower()
    
    # Allowed categories
    ALLOWED_CATEGORIES = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    
    # Severity keywords triggering 'Urgent'
    SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    category = "Other"
    priority = "Low"
    flag = ""
    reason = "Description not provided or parseable."

    if not desc:
        return {
            'complaint_id': row.get('complaint_id', ''),
            'category': "Other",
            'priority': "Low",
            'reason': "Missing description.",
            'flag': "NEEDS_REVIEW"
        }

    # Extract Category
    if any(w in desc_lower for w in ['pothole']):
        category = "Pothole"
    elif any(w in desc_lower for w in ['flood']):
        category = "Flooding"
    elif any(w in desc_lower for w in ['light', 'dark']):
        category = "Streetlight"
    elif any(w in desc_lower for w in ['waste', 'garbage', 'dump']):
        category = "Waste"
    elif any(w in desc_lower for w in ['noise', 'music']):
        category = "Noise"
    elif any(w in desc_lower for w in ['road surface', 'crack']):
        category = "Road Damage"
    elif any(w in desc_lower for w in ['heritage']):
        category = "Heritage Damage"
    elif any(w in desc_lower for w in ['drain']):
        category = "Drain Blockage"
    elif any(w in desc_lower for w in ['heat']):
        category = "Heat Hazard"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Evaluate priority
    has_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if has_severity:
        priority = "Urgent"
    elif category in ["Flooding", "Road Damage", "Drain Blockage", "Streetlight"]:
        priority = "Standard"
    else:
        priority = "Low"

    # Generate reason citing words
    cited_words = []
    if has_severity:
        cited_words.extend(has_severity)
    
    # Add category-related words
    for word in desc.split():
        clean_word = re.sub(r'[^\w\s]', '', word.lower())
        if clean_word in ['pothole', 'flood', 'flooded', 'light', 'lights', 'waste', 'garbage', 'dumped', 'music', 'crack', 'cracked', 'drain', 'heritage']:
            cited_words.append(clean_word)
            
    cited_words = list(set(cited_words))
    
    if cited_words:
        reason = f"Classified based on keywords: {', '.join(cited_words)}."
    else:
        reason = "Classified based on general context as no specific keywords matched."

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
    # Safe counting of successes vs failures
    processed = 0
    failed = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as fin, \
             open(output_path, 'w', newline='', encoding='utf-8') as fout:
            reader = csv.DictReader(fin)
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                    processed += 1
                except Exception as e:
                    print(f"Failed to process row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    failed += 1
    except Exception as e:
        print(f"Error accessing files: {e}")
        
    print(f"Processed {processed} rows. Failed {failed} rows.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
