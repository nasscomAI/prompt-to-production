"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = row.get('description', '').lower()
    
    # Category classification based on keywords
    category_keywords = {
        'Pothole': ['pothole', 'hole in road'],
        'Flooding': ['flood', 'water logging', 'drain overflow'],
        'Streetlight': ['streetlight', 'light not working'],
        'Waste': ['waste', 'garbage', 'dump'],
        'Noise': ['noise', 'loud', 'disturbance'],
        'Road Damage': ['road damage', 'crack', 'pavement'],
        'Heritage Damage': ['heritage', 'monument damage'],
        'Heat Hazard': ['heat', 'hot', 'temperature'],
        'Drain Blockage': ['drain block', 'clogged drain'],
    }
    
    category = 'Other'
    for cat, keywords in category_keywords.items():
        if any(keyword in description for keyword in keywords):
            category = cat
            break
    
    # Priority based on severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Urgent' if any(keyword in description for keyword in severity_keywords) else 'Standard'
    
    # Reason citing specific words
    reason = f"Description contains keywords related to {category.lower()}."
    
    # Flag for ambiguity
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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Log error and skip bad row
                    print(f"Error processing row {row}: {e}")
                    results.append({
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Error in processing',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Input file {input_path} not found.")
        return
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['complaint_id', 'category', 'priority', 'reason', 'flag'])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
