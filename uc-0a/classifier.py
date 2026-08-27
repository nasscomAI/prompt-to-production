"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Define categorization keywords for strict matching
CATEGORY_KEYWORDS = {
    'Pothole': ['pothole'],
    'Flooding': ['flood', 'water'],
    'Streetlight': ['streetlight', 'dark', 'lights out'],
    'Waste': ['garbage', 'waste', 'dump', 'dead animal', 'smell'],
    'Noise': ['music', 'noise', 'loud'],
    'Road Damage': ['road surface', 'crack', 'sinking', 'broken', 'upturned'],
    'Heritage Damage': ['heritage'],
    'Heat Hazard': ['heat'],
    'Drain Blockage': ['drain block', 'drain', 'manhole']
}

# Define severity keywords that trigger 'Urgent' priority
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md and skills.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # --- 1. Priority Enforcement ---
    priority = 'Standard'
    severity_trigger = None
    
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = 'Urgent'
            severity_trigger = keyword
            break
            
    # --- 2. Category Enforcement ---
    matched_categories = []
    category_trigger = None
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                matched_categories.append(cat)
                category_trigger = kw
                break
                
    # Remove duplicates
    matched_categories = list(set(matched_categories))
    
    # Handle ambiguity and exact schema matching
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ''
    else:
        # Ambiguous or no matches
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        if not matched_categories:
            category_trigger = 'no relevant keywords'
        else:
            category_trigger = 'multiple conflicting keywords'

    # --- 3. Reason Enforcement (Exactly one sentence citing specific words) ---
    if priority == 'Urgent':
        reason = f"Priority was escalated to Urgent because the description explicitly mentions '{severity_trigger}'."
    elif category == 'Other':
        reason = f"Category is Other and requires review because the description contains {category_trigger}."
    else:
        reason = f"Classified as {category} because the description specifically mentions '{category_trigger}'."

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
    fieldnames = []
    out_rows = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if reader.fieldnames:
                fieldnames = list(reader.fieldnames)
            else:
                fieldnames = ['complaint_id', 'description']
                
            # Ensure our output columns exist in the header
            for new_col in ['category', 'priority', 'reason', 'flag']:
                if new_col not in fieldnames:
                    fieldnames.append(new_col)
                    
            for row in reader:
                try:
                    # Apply our classify skill
                    result = classify_complaint(row)
                    
                    # Update row with results
                    row.update(result)
                    out_rows.append(row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                    row['flag'] = 'ERROR'
                    out_rows.append(row)
                    
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)
            
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
    except Exception as e:
        print(f"Fatal error during batch classification: {e}")


if __name__ == "__main__":
    import os
    import glob
    
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=False, help="Path to test_[city].csv")
    parser.add_argument("--output", required=False, help="Path to write results CSV")
    parser.add_argument("--all", action="store_true", help="Process all cities in data/city-test-files")
    args = parser.parse_args()
    
    if args.all:
        input_dir = os.path.join("..", "data", "city-test-files")
        csv_files = glob.glob(os.path.join(input_dir, "test_*.csv"))
        
        if not csv_files:
            print(f"No test files found in {input_dir}")
        else:
            print(f"Found {len(csv_files)} city files. Processing...")
            for input_path in csv_files:
                filename = os.path.basename(input_path)
                city_name = filename.replace("test_", "").replace(".csv", "")
                output_path = f"results_{city_name}.csv"
                print(f"-> Processing {city_name}...")
                batch_classify(input_path, output_path)
            print("Done processing all cities.")
            
    elif args.input and args.output:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
    else:
        print("Please provide either --all to process all cities, or --input and --output for a single file.")