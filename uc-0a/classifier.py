"""
UC-0A — Complaint Classifier
Built using the rules defined in agents.md and skills.md.
"""
import argparse
import csv

# Enforcement Rules from agents.md
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CATEGORIES = {
    'Pothole': ['pothole', 'crater'],
    'Flooding': ['flood', 'water', 'rain'],
    'Streetlight': ['streetlight', 'light', 'dark'],
    'Waste': ['garbage', 'waste', 'smell', 'animal'],
    'Noise': ['music', 'noise', 'loud'],
    'Road Damage': ['cracked', 'sinking', 'tiles broken', 'road surface', 'footpath'],
    'Heritage Damage': ['heritage'],
    'Heat Hazard': ['heat', 'hot'],
    'Drain Blockage': ['drain', 'block'],
}

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint to determine its category, priority, reason, and review flag.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # Priority Enforcement
    priority = "Standard"
    found_severity_keywords = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            found_severity_keywords.append(keyword)
            priority = "Urgent"
            
    # Category Enforcement
    matched_categories = []
    matched_category_keywords = []
    
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_category_keywords.append(kw)
                
    # Ambiguity Check & Reasoning Enforcement
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = f"Classified as {category} because description explicitly mentions '{matched_category_keywords[0]}'."
    elif len(matched_categories) > 1:
        # If multiple categories match, it is ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous complaint mentioning multiple issues: {', '.join(matched_category_keywords)}."
    else:
        # If no categories match, it is ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently determine category from the description alone."
        
    # Append priority reasoning if Urgent
    if priority == "Urgent":
        reason += f" Priority is Urgent due to severity keyword(s): {', '.join(found_severity_keywords)}."
        
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV file of complaints, applies classify_complaint to each row, 
    and writes the results to an output CSV file.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # Ensure output columns exist
            if 'category' not in fieldnames: fieldnames.append('category')
            if 'priority' not in fieldnames: fieldnames.append('priority')
            if 'reason' not in fieldnames: fieldnames.append('reason')
            if 'flag' not in fieldnames: fieldnames.append('flag')
                
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    # Don't crash on bad rows
                    row.update({'category': '', 'priority': '', 'reason': f'Error: {str(e)}', 'flag': 'ERROR'})
                    results.append(row)
                    
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
