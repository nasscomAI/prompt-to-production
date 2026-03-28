"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Enforcement Rule 2: Priority must be Urgent if specific severity keywords present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severity = [kw for kw in severity_keywords if kw in desc]
    
    if found_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Enforcement Rule 1: Category must strictly map to allowed values
    category_map = {
        'pothole': 'Pothole',
        'crater': 'Pothole',
        'flood': 'Flooding',
        'water': 'Flooding',
        'streetlight': 'Streetlight',
        'light': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'road damage': 'Road Damage',
        'cracked': 'Road Damage',
        'broken': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain': 'Drain Blockage',
        'manhole': 'Drain Blockage'
    }

    matched_categories = set()
    mapped_kws = []
    for kw, cat in category_map.items():
        if kw in desc:
            matched_categories.add(cat)
            mapped_kws.append(kw)

    # Enforcement Rule 4 (Refusal Condition): Handle ambiguity
    flag = ""
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Enforcement Rule 3: Detail reason citing specific words
    reasons = []
    if mapped_kws:
        reasons.append(f"Matched category based on keywords: {', '.join(mapped_kws)}.")
    if found_severity:
        reasons.append(f"Marked Urgent priority due to severity keyword(s): {', '.join(found_severity)}.")
        
    reason = " ".join(reasons) if reasons else "Categorized as Other / Needs Review due to lack of distinct context."

    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle errors gracefully and process all valid rows.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            fieldnames = list(reader.fieldnames or [])
            
            if not fieldnames:
                print("Error: Input CSV is empty or invalid.")
                return
                
            # Add output columns if missing
            output_cols = ['category', 'priority', 'reason', 'flag']
            for col in output_cols:
                if col not in fieldnames:
                    fieldnames.append(col)
                    
            with open(output_path, 'w', encoding='utf-8', newline='') as fout:
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()
                
                processed_count = 0
                for row in reader:
                    try:
                        classification = classify_complaint(row)
                        row.update(classification)
                        writer.writerow(row)
                        processed_count += 1
                    except Exception as e:
                        # Error handling matching skills.md
                        print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                        row.update({
                            'category': 'Other',
                            'priority': 'Standard',
                            'reason': f"Classification failed: {str(e)}",
                            'flag': 'ERROR'
                        })
                        writer.writerow(row)
                        
                print(f"Successfully processed {processed_count} rows.")
                        
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
