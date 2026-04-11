"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # 1. Priority Enforcement
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_severity = [kw for kw in severity_keywords if kw in desc]
    priority = 'Urgent' if matched_severity else 'Standard'
    
    # 2. Category Taxonomy Enforcements
    taxonomy = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'knee-deep'],
        'Streetlight': ['streetlight', 'lights out', 'dark', 'sparking'],
        'Waste': ['garbage', 'dump', 'waste', 'animal'],
        'Noise': ['music', 'noise', 'loud'],
        'Road Damage': ['road surface', 'crack', 'sinking', 'footpath', 'manhole'],
        'Heritage Damage': ['heritage'],
        'Heat Hazard': ['heat'],
        'Drain Blockage': ['drain']
    }
    
    matched_categories = set()
    cited_words = []
    
    for cat, kws in taxonomy.items():
        for kw in kws:
            if kw in desc:
                matched_categories.add(cat)
                cited_words.append(kw)
                
    # 3. Handle rules & ambiguity (flag)
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        word = cited_words[0]
        # Ambiguity check (e.g., heritage and streetlights could cross over)
        if category == 'Streetlight' and 'heritage' in desc:
            category = 'Other'
            flag = 'NEEDS_REVIEW'
            reason = "Ambiguous description mentioning both streetlights and heritage."
        else:
            flag = ''
            if matched_severity:
                reason = f"Assigned to {category} with {priority} priority due to the description explicitly mentioning '{word}' and '{matched_severity[0]}'."
            else:
                reason = f"Assigned to {category} because the description contains the word '{word}'."
                
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        if len(matched_categories) > 1:
            reason = f"The description matches multiple categories citing '{cited_words[0]}' and '{cited_words[1]}'."
        elif matched_severity:
            reason = f"The category is ambiguous, but marked {priority} because it mentions '{matched_severity[0]}'."
        else:
            reason = "Unable to distinctly map the text to any standardized category."

    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    row.update(classified)
                except Exception as e:
                    print(f"Row error: {e}")
                    row.update({'category': 'Other', 'priority': 'Standard', 'reason': 'Failed processing.', 'flag': 'NEEDS_REVIEW'})
                results.append(row)
    except Exception as e:
        print(f"Failed reading {input_path}: {e}")
        return

    if not results:
        print("No valid data to output.")
        return

    for col in ['category', 'priority', 'reason', 'flag']:
        if col not in fieldnames:
            fieldnames.append(col)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed writing {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
