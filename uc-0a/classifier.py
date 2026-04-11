"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import re
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with added keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Evaluate Priority (Urgent if severity keywords present)
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    found_severity_word = None
    
    for word in severity_keywords:
        if re.search(rf'\b{word}s?\b', desc):
            priority = "Urgent"
            found_severity_word = word
            break
            
    # 2. Evaluate Category
    category_mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "rain": "Flooding",
        "water": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "smell": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "crack": "Road Damage",
        "sinking": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "manhole": "Drain Blockage",
        "drain": "Drain Blockage"
    }
    
    category = "Other"
    flag = ""
    found_cat_word = None
    
    for kw, cat in category_mapping.items():
        if re.search(rf'\b{kw}s?\b', desc):
            category = cat
            found_cat_word = kw
            break
            
    # 3. Handle ambiguity and flags
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    if "heritage" in desc and "light" in desc:
        flag = "NEEDS_REVIEW"
        
    # 4. Synthesize Reason Sentence
    if found_severity_word and found_cat_word:
        reason = f"Classified as {category} and {priority} because description mentions '{found_cat_word}' and '{found_severity_word}'."
    elif found_cat_word:
        reason = f"Classified as {category} and {priority} because description mentions '{found_cat_word}'."
    elif found_severity_word:
        reason = f"Classified as {category} and {priority} because description mentions '{found_severity_word}'."
    else:
        reason = f"Placed in {category} with {priority} priority as no specific known keywords were found in the description."

    row['category'] = category
    row['priority'] = priority
    row['reason'] = reason
    row['flag'] = flag
    
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fieldnames = list(reader.fieldnames)
                for col in ['category', 'priority', 'reason', 'flag']:
                    if col not in fieldnames:
                        fieldnames.append(col)
                        
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping malformed row due to error: {e}")
                    row['flag'] = "ERROR"
                    results.append(row)
    except Exception as e:
        print(f"Failed to read input file {input_path}: {e}")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
