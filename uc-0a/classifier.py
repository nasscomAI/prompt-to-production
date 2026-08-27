"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E. enforcement rules.
    Returns: dict with all required output fields.
    """
    desc = str(row.get('description', '')).lower()
    complaint_id = row.get('id', 'Unknown')
    
    # 1. Define Taxonomy & Keywords
    categories = {
        'Pothole': ['pothole', 'hole', 'cracked'],
        'Flooding': ['flood', 'water logging', 'heavy rain', 'submerged'],
        'Streetlight': ['light', 'dark', 'bulb', 'streetlight'],
        'Waste': ['garbage', 'trash', 'waste', 'smell', 'dump', 'stink'],
        'Noise': ['noise', 'loud', 'sound', 'music', 'blasting'],
        'Road Damage': ['road', 'asphalt', 'surface', 'pavement', 'tar'],
        'Heritage Damage': ['heritage', 'monument', 'temple', 'statue', 'historic'],
        'Heat Hazard': ['heat', 'sun', 'extreme hot', 'shade', 'wave'],
        'Drain Blockage': ['drain', 'sewer', 'clogged', 'overflow', 'gutter']
    }
    
    # 2. Determine Category
    detected_category = 'Other'
    flag = ''
    found_keywords = []
    
    for category, keywords in categories.items():
        matches = [k for k in keywords if k in desc]
        if matches:
            detected_category = category
            found_keywords.extend(matches)
            break
            
    if detected_category == 'Other':
        flag = 'NEEDS_REVIEW'

    # 3. Determine Priority (Severity Enforcements)
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    severity_matches = [k for k in severity_keywords if k in desc]
    
    if severity_matches:
        priority = 'Urgent'
        found_keywords.extend(severity_matches)
    
    # 4. Generate Reason (Citing specific words)
    if found_keywords:
        reason = f"Classified as {detected_category} with {priority} priority due to presence of: {', '.join(set(found_keywords))}."
    else:
        reason = "Placed in Other category for manual review due to lack of specific taxonomy keywords."

    return {
        'id': complaint_id,
        'description': row.get('description', ''),
        'category': detected_category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Processes the input CSV batch-wise, ensuring robustness and failure tolerance.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    if not row.get('description'):
                        print(f"Skipping row {row.get('id', 'N/A')}: No description found.")
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('id', 'Unknown')}: {e}")
                    
        if not results:
            print("No valid rows were processed.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Critial Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
