"""
UC-0A — Complaint Classifier
Implemented based on agents.md and skills.md using RICE workflow.
"""
import argparse
import csv
import json

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description.
    Returns: dict with keys: category, priority, reason, flag

    Enforces agents.md rules: exact categories, urgency on keywords, cited reasons, ambiguity flags.
    """
    desc_lower = description.lower()

    # Category classification based on keywords (exact matches to prevent drift)
    categories = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'water', 'rain', 'overflow'],
        'Streetlight': ['streetlight', 'light', 'bulb', 'lamp'],
        'Waste': ['waste', 'garbage', 'trash', 'dump'],
        'Noise': ['noise', 'loud', 'sound', 'music'],
        'Road Damage': ['road', 'damage', 'crack', 'broken'],
        'Heritage Damage': ['heritage', 'monument', 'historical', 'damage'],
        'Heat Hazard': ['heat', 'hot', 'temperature', 'sun'],
        'Drain Blockage': ['drain', 'block', 'clog', 'sewage'],
    }

    category = 'Other'
    for cat, keywords in categories.items():
        if any(keyword in desc_lower for keyword in keywords):
            category = cat
            break

    # Priority: Urgent if severity keywords present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Urgent' if any(word in desc_lower for word in severity_keywords) else 'Standard'

    # Reason: One sentence citing specific words
    cited_words = [word for word in categories.get(category, []) if word in desc_lower]
    if cited_words:
        reason = f"The description contains '{cited_words[0]}' which indicates a {category} issue."
    else:
        reason = f"The description suggests a {category} issue based on context."

    # Flag: NEEDS_REVIEW if genuinely ambiguous (e.g., category Other or conflicting keywords)
    flag = 'NEEDS_REVIEW' if category == 'Other' or len([cat for cat, kw in categories.items() if any(k in desc_lower for k in kw)]) > 1 else ''

    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row using classify_complaint, write results CSV.

    Handles errors gracefully: skips invalid rows, logs issues, ensures output is produced.
    """
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    results = []
    for row in rows:
        complaint_id = row.get('complaint_id', 'unknown')
        description = row.get('description', '')
        if not description:
            print(f"Warning: Skipping row {complaint_id} - missing description.")
            continue
        try:
            classification = classify_complaint(description)
            result_row = {
                'complaint_id': complaint_id,
                'description': description,
                **classification
            }
            results.append(result_row)
        except Exception as e:
            print(f"Error classifying row {complaint_id}: {e}")
            # Still add with defaults
            results.append({
                'complaint_id': complaint_id,
                'description': description,
                'category': 'Other',
                'priority': 'Standard',
                'reason': 'Classification failed due to error.',
                'flag': 'NEEDS_REVIEW'
            })

    # Write output CSV
    if results:
        fieldnames = ['complaint_id', 'description', 'category', 'priority', 'reason', 'flag']
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing output file: {e}")
    else:
        print("No valid rows to write.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
