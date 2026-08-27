"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # 1. Determine Priority
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_urgent_kws = [kw for kw in urgent_keywords if kw in desc]
    priority = "Urgent" if matched_urgent_kws else "Standard"
    
    # 2. Determine Category Mapping
    cat_keywords = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'water'],
        'Streetlight': ['streetlight', 'light', 'dark', 'sparking'],
        'Waste': ['waste', 'garbage', 'trash', 'animal', 'smell'],
        'Noise': ['noise', 'music', 'loud'],
        'Road Damage': ['crack', 'sinking', 'footpath', 'tiles'],
        'Heritage Damage': ['heritage'],
        'Heat Hazard': ['heat'],
        'Drain Blockage': ['drain', 'manhole', 'sewer']
    }
    
    matched_cats = {}
    for cat, kws in cat_keywords.items():
        for kw in kws:
            if kw in desc:
                matched_cats[cat] = kw
                break
                
    flag = ""
    # 3. Handle Ambiguity & Formatting
    if len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        keyword = list(matched_cats.values())[0]
        reason = f"Classified as {category} because description mentions '{keyword}'."
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous description containing keywords for multiple categories: {', '.join(matched_cats.keys())}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not determine a specific category from the description alone."
        
    if priority == "Urgent":
        reason += f" Priority is Urgent due to severity keyword '{matched_urgent_kws[0]}'."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely handles malformed rows and ensures all columns exist.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            
            # Ensure our new classification fields exist in the output CSV headers
            for field in ['category', 'priority', 'reason', 'flag']:
                if field not in fieldnames:
                    fieldnames.append(field)
                    
            rows = []
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    row.update(classified)
                except Exception as e:
                    # Fallback for completely unparseable rows
                    row['category'] = 'Other'
                    row['priority'] = 'Standard'
                    row['flag'] = 'NEEDS_REVIEW'
                    row['reason'] = f"Error during classification: {str(e)}"
                rows.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error processing batch: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
