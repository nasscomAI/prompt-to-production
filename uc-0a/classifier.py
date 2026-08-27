"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').lower()
    
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'No description provided',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Determine category
    category = 'Other'
    reason_word = ''
    
    if 'pothole' in description:
        category = 'Pothole'
        reason_word = 'pothole'
    elif 'flood' in description or 'water' in description:
        category = 'Flooding'
        reason_word = 'flood' if 'flood' in description else 'water'
    elif 'heritage' in description and ('damage' in description or 'broken' in description or 'lights' in description):
        category = 'Heritage Damage'
        reason_word = 'heritage'
    elif 'streetlight' in description or 'light' in description:
        category = 'Streetlight'
        reason_word = 'streetlight' if 'streetlight' in description else 'light'
    elif 'waste' in description or 'garbage' in description or 'trash' in description or 'animal' in description:
        category = 'Waste'
        reason_word = 'waste' if 'waste' in description else 'garbage' if 'garbage' in description else 'trash' if 'trash' in description else 'animal'
    elif 'noise' in description or 'music' in description or 'loud' in description:
        category = 'Noise'
        reason_word = 'noise' if 'noise' in description else 'music' if 'music' in description else 'loud'
    elif 'road damage' in description or 'crack' in description or 'pavement' in description or 'manhole' in description or 'cover' in description or 'broken' in description or 'upturned' in description:
        category = 'Road Damage'
        reason_word = 'road damage' if 'road damage' in description else 'crack' if 'crack' in description else 'pavement' if 'pavement' in description else 'manhole' if 'manhole' in description else 'cover' if 'cover' in description else 'broken' if 'broken' in description else 'upturned'
    elif 'heat' in description or 'temperature' in description:
        category = 'Heat Hazard'
        reason_word = 'heat' if 'heat' in description else 'temperature'
    elif 'drain' in description or 'blockage' in description:
        category = 'Drain Blockage'
        reason_word = 'drain' if 'drain' in description else 'blockage'
    
    # Determine priority
    priority = 'Standard'
    urgent_trigger = None
    for keyword in URGENT_KEYWORDS:
        if keyword in description:
            priority = 'Urgent'
            urgent_trigger = keyword
            break
    
    # If category is Other and no urgent, maybe Low
    if category == 'Other' and priority == 'Standard':
        priority = 'Low'
    
    # Reason
    if urgent_trigger:
        reason = f"Classified as {category} with {priority} priority because description mentions '{reason_word}' and '{urgent_trigger}'."
    else:
        reason = f"Classified as {category} with {priority} priority because description mentions '{reason_word}'."
    
    # Flag
    flag = 'NEEDS_REVIEW' if category == 'Other' else ''
    
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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
                    # Add error row
                    results.append({
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f'Classification failed: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Input file {input_path} not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Write output
    if results:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing output file: {e}")
    else:
        print("No results to write.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
