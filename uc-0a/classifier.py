"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E. enforcement rules.
    """
    description = (row.get('description') or "").lower()
    
    # Priority logic: Urgent if severity keywords present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Urgent" if any(k in description for k in severity_keywords) else "Standard"

    # Category logic: Strict list from agents.md
    category_map = {
        'Pothole': ['pothole', 'pitted'],
        'Flooding': ['flood', 'water', 'submerged'],
        'Streetlight': ['streetlight', 'light', 'dark', 'lamp'],
        'Waste': ['garbage', 'waste', 'trash', 'dump', 'smell', 'bins', 'animal'],
        'Noise': ['noise', 'music', 'loud', 'sound', 'midnight'],
        'Road Damage': ['cracked', 'sinking', 'asphalt', 'road surface'],
        'Heritage Damage': ['heritage', 'historic', 'monument'],
        'Heat Hazard': ['heat', 'temperature', 'sun'],
        'Drain Blockage': ['drain', 'sewer', 'manhole', 'overflow'],
    }

    found_category = "Other"
    reason = "No specific category keywords found in description."
    
    for cat, keywords in category_map.items():
        for k in keywords:
            if k in description:
                found_category = cat
                reason = f"Classification based on presence of word: '{k}'."
                break
        if found_category != "Other":
            break
            
    # Flag logic: NEEDS_REVIEW if Other
    flag = "NEEDS_REVIEW" if found_category == "Other" else ""
    
    return {
        'category': found_category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle nulls/missing descriptions gracefully
                if not row.get('description'):
                    continue
                
                classification = classify_complaint(row)
                row.update(classification)
                results.append(row)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if not results:
        print("No results to process.")
        return

    # Write output CSV
    fieldnames = list(results[0].keys())
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
