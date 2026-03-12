"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

HIGH_SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint_category(description: str) -> str:
    description_lower = description.lower()
    
    if any(word in description_lower for word in ['pothole']):
        return "Pothole"
    
    if any(word in description_lower for word in ['flood', 'rain', 'water']):
        return "Flooding"
        
    if any(word in description_lower for word in ['streetlight', 'dark', 'light']):
        return "Streetlight"
        
    if any(word in description_lower for word in ['garbage', 'waste', 'smell', 'dump']):
        return "Waste"
        
    if any(word in description_lower for word in ['music', 'noise', 'loud']):
        return "Noise"
        
    if any(word in description_lower for word in ['road', 'crack', 'sinking']):
        return "Road Damage"
        
    if any(word in description_lower for word in ['heritage']):
        return "Heritage Damage"

    if any(word in description_lower for word in ['drain']):
        return "Drain Blockage"
        
    return "Other"

def assess_complaint_priority(description: str) -> str:
    description_lower = description.lower()
    for keyword in HIGH_SEVERITY_KEYWORDS:
        if keyword in description_lower:
            return "Urgent"
    return "Standard"

def extract_reasoning_keywords(description: str, category: str, priority: str) -> str:
    description_lower = description.lower()
    
    # Priority reasons
    priority_reason = ""
    for keyword in HIGH_SEVERITY_KEYWORDS:
        if keyword in description_lower:
            priority_reason = f"contains severe keyword '{keyword}'"
            break
            
    # Basic category explanation
    reason = f"Mentioned terms related to {category}"
    if priority_reason:
        reason += f" and {priority_reason}"
        
    return reason


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '')
    if not description:
        return {
            'complaint_id': row.get('complaint_id', 'UNKNOWN'),
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW'
        }

    category = classify_complaint_category(description)
    priority = assess_complaint_priority(description)
    reason = extract_reasoning_keywords(description, category, priority)
    
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    results.append({
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Processing error',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
        
    if not results:
        print("No results to write. Output file not created.")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
