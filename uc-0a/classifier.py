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
    desc = row.get('description', '').lower()
    
    # Priority keywords that MUST trigger Urgent
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    priority = "Standard"
    reason_words = []
    
    # Check for urgent keywords
    urgent_found = [kw for kw in urgent_keywords if kw in desc]
    if urgent_found:
        priority = "Urgent"
        reason_words.extend(urgent_found)
    
    # Category hints
    cat_hints = {
        'Pothole': ['pothole'],
        'Flooding': ['flood'],
        'Streetlight': ['streetlight', 'lights out'],
        'Waste': ['waste', 'garbage', 'dead animal'],
        'Noise': ['music', 'noise', 'loud'],
        'Road Damage': ['crack', 'manhole', 'footpath'],
        'Heritage Damage': ['heritage'],
        'Heat Hazard': ['heat wave'],
        'Drain Blockage': ['drain block']
    }
    
    matched_categories = []
    for cat, hints in cat_hints.items():
        for hint in hints:
            if hint in desc:
                matched_categories.append(cat)
                reason_words.append(hint)
                break
                
    # Unique matched categories
    matched_categories = list(dict.fromkeys(matched_categories))
    
    flag = ''
    category = 'Other'
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Ambiguous category
        flag = 'NEEDS_REVIEW'
        category = 'Other'
    else:
        # No clear category found
        flag = 'NEEDS_REVIEW'
        category = 'Other'
        
    # Reason construction (one sentence) citing specific exact words
    if not reason_words:
        reason = "No specific classification identifiers were found in the description."
    else:
        cited_words = ", ".join(f"'{w}'" for w in list(dict.fromkeys(reason_words)))
        reason = f"The complaint was classified due to the presence of terms: {cited_words}."
        
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        result = classify_complaint(row)
                        writer.writerow(result)
                    except Exception as e:
                        logging.error(f"Error classifying row {row_num}: {e}")
                        writer.writerow({
                            'complaint_id': row.get('complaint_id', ''),
                            'category': 'Other',
                            'priority': 'Low',
                            'reason': 'Error occurred during classification.',
                            'flag': 'NEEDS_REVIEW'
                        })
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}. Raising error.")
        raise
    except Exception as e:
        logging.error(f"Failed to process batch classification: {e}. Raising error.")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
