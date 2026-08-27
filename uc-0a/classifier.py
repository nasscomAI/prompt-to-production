"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import logging

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    complaint_id = row.get('complaint_id', '')

    category = "Other"
    priority = "Standard"
    reason = "No specific match found"
    flag = ""

    # Determine Category based on keywords mapping directly to the 10 allowed strings
    if any(word in desc for word in ['pothole', 'crater']):
        category = "Pothole"
        reason = "Description matched 'pothole' or 'crater'."
    elif any(word in desc for word in ['flood', 'water logging', 'overflow', 'submerge', 'water']):
        category = "Flooding"
        reason = "Description matched flooding-related keywords."
    elif any(word in desc for word in ['drain', 'sewer', 'blockage', 'clog', 'gutter']):
        category = "Drain Blockage"
        reason = "Description matched drain or sewer blockage keywords."
    elif any(word in desc for word in ['light', 'dark', 'bulb', 'streetlight', 'lamp', 'illumination']):
        category = "Streetlight"
        reason = "Description matched streetlight or lighting keywords."
    elif any(word in desc for word in ['trash', 'garbage', 'waste', 'dump', 'litter', 'rubbish']):
        category = "Waste"
        reason = "Description matched waste or garbage keywords."
    elif any(word in desc for word in ['noise', 'loud', 'music', 'sound', 'bark']):
        category = "Noise"
        reason = "Description matched noise or loud sound keywords."
    elif any(word in desc for word in ['road', 'crack', 'pavement', 'asphalt']):
        category = "Road Damage"
        reason = "Description matched road damage or pavement keywords."
    elif any(word in desc for word in ['heritage', 'monument', 'statue', 'historical', 'ancient']):
        category = "Heritage Damage"
        reason = "Description matched historical or heritage monument keywords."
    elif any(word in desc for word in ['heat', 'temperature', 'sunstroke', 'shade', 'hot']):
        category = "Heat Hazard"
        reason = "Description matched heat hazard or high temperature keywords."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Determine Priority (Urgent, Standard, Low)
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_urgent_words = [word for word in urgent_keywords if word in desc]
    
    if found_urgent_words:
        priority = "Urgent"
        # Overwrite or append to reason explaining the escalation
        reason += f" Escalated to Urgent because it mentions: {', '.join(found_urgent_words)}."

    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    if not row.get('description') or not str(row.get('description')).strip():
                        results.append({
                            'complaint_id': row.get('complaint_id', 'Unknown'),
                            'category': 'Other',
                            'priority': 'Standard',
                            'reason': 'Missing or invalid description.',
                            'flag': 'NEEDS_REVIEW'
                        })
                        continue
                        
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    logging.error(f"Error processing row {row}: {e}")
                    results.append({
                        'complaint_id': row.get('complaint_id', 'Unknown'),
                        'category': 'Error',
                        'priority': 'Standard',
                        'reason': f'System error processing row: {str(e)}',
                        'flag': 'FAILED'
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
