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
    complaint_id = row.get('complaint_id', '')

    # Define categories and keywords - must match allowed values from enforcement
    categories = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'water', 'drain', 'floods', 'flooding'],
        'Streetlight': ['streetlight', 'light', 'lights'],
        'Garbage': ['garbage', 'bin', 'waste', 'overflow'],
        'Noise': ['noise', 'music', 'sound'],
        'Road Damage': ['crack', 'sinking', 'damage', 'surface', 'broken', 'tiles']
    }

    category = 'Other'
    reason_words = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                category = cat
                reason_words.append(kw)
                break
        if category != 'Other':
            break

    if category == 'Other':
        flag = 'NEEDS_REVIEW'
        reason = "No matching keywords found in description"
    else:
        flag = ''
        reason = f"Keywords found: {', '.join(reason_words)}"

    # Priority
    urgent_words = ['injury', 'child', 'school', 'emergency', 'accident', 'risk']
    priority = 'Urgent' if any(word in description for word in urgent_words) else 'Normal'

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
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # For bad rows, create a result with Other and flag
                    complaint_id = row.get('complaint_id', 'unknown')
                    results.append({
                        'complaint_id': complaint_id,
                        'category': 'Other',
                        'priority': 'Normal',
                        'reason': f'Error processing row: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except Exception as e:
        # If input file error, perhaps write empty or error
        pass

    # Write output
    if results:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
