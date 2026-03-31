import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    desc_lower = description.lower()
    complaint_id = row.get('complaint_id', '')

    category = 'Other'
    flag = 'NEEDS_REVIEW'

    category_map = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'water': 'Flooding',
        'streetlight': 'Streetlight',
        'light': 'Streetlight',
        'dark': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'dump': 'Waste',
        'animal': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'crack': 'Road Damage',
        'footpath': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain': 'Drain Blockage',
        'manhole': 'Drain Blockage'
    }
    
    priority_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    # Check for category
    found_cat_kw = None
    for kw, cat in category_map.items():
        if kw in desc_lower:
            category = cat
            found_cat_kw = kw
            flag = ''
            break
            
    # Check for priority
    priority = 'Standard'
    found_pri_kw = None
    for kw in priority_keywords:
        if kw in desc_lower:
            priority = 'Urgent'
            found_pri_kw = kw
            break
            
    # Format reason sentence
    reason_parts = []
    if found_cat_kw:
        reason_parts.append(f"Categorized as {category} because of '{found_cat_kw}'")
    else:
        reason_parts.append("Categorized as Other because no known keywords were found")
        
    if found_pri_kw:
        reason_parts.append(f"marked Urgent due to '{found_pri_kw}'")
    else:
        reason_parts.append("marked Standard as no severity keywords apply")
        
    reason = " and ".join(reason_parts) + "."

    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV of complaints, applies classify_complaint per row, and writes an output CSV.
    Must flag nulls gracefully, not crash on malformed rows, and ensure output is produced even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Input CSV is empty or has no headers.")
                return
                
            out_fieldnames = list(fieldnames) + ['category', 'priority', 'reason', 'flag']
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    # Gracefully handle null or essentially empty rows
                    if not row or not any(row.values()):
                        continue
                        
                    try:
                        classification = classify_complaint(row)
                        out_row = dict(row)
                        out_row['category'] = classification.get('category', 'Other')
                        out_row['priority'] = classification.get('priority', 'Low')
                        out_row['reason'] = classification.get('reason', '')
                        out_row['flag'] = classification.get('flag', '')
                        writer.writerow(out_row)
                    except Exception as e:
                        # Log and keep writing others if one fails
                        print(f"Error processing row with ID {row.get('complaint_id', 'Unknown')}: {e}")
                        out_row = dict(row)
                        out_row['category'] = 'Other'
                        out_row['priority'] = 'Low'
                        out_row['reason'] = f'Error: {str(e)}'
                        out_row['flag'] = 'NEEDS_REVIEW'
                        writer.writerow(out_row)
                        
    except Exception as e:
        print(f"Failed to process files: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
