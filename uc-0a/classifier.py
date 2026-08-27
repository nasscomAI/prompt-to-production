"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').strip()
    complaint_id = row.get('complaint_id', 'Unknown')

    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Empty description',
            'flag': 'NEEDS_REVIEW'
        }

    # Allowed categories
    categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    
    # Severity keywords for Urgent priority
    severity_keywords = [
        'injury', 'child', 'school', 'hospital', 'ambulance', 
        'fire', 'hazard', 'fell', 'collapse'
    ]

    # Simple rule-based classification for the starter implementation
    # In a real scenario, this would call an LLM with the prompt from agents.md
    desc_lower = description.lower()
    
    # Determine Category
    category = "Other"
    if "pothole" in desc_lower: category = "Pothole"
    elif "flood" in desc_lower or "waterlogging" in desc_lower: category = "Flooding"
    elif "light" in desc_lower or "dark" in desc_lower: category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower: category = "Waste"
    elif "noise" in desc_lower or "loud" in desc_lower: category = "Noise"
    elif "road" in desc_lower and ("damage" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower): category = "Road Damage"
    elif "heritage" in desc_lower or "monument" in desc_lower: category = "Heritage Damage"
    elif "heat" in desc_lower or "temperature" in desc_lower: category = "Heat Hazard"
    elif "drain" in desc_lower or "sewage" in desc_lower or "manhole" in desc_lower: category = "Drain Blockage"

    # Determine Priority
    priority = "Standard"
    if any(kw in desc_lower for kw in severity_keywords):
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"

    # Determine Reason (Citing words)
    reason = "Classified based on description content."
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging"],
        "Streetlight": ["light", "dark"],
        "Waste": ["garbage", "waste", "trash"],
        "Noise": ["noise", "loud"],
        "Road Damage": ["road", "damage", "cracked", "sinking"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "temperature"],
        "Drain Blockage": ["drain", "sewage", "manhole"]
    }
    
    if category in category_keywords:
        for kw in category_keywords[category]:
            if kw in desc_lower:
                reason = f"Contains keyword '{kw}'"
                break
    elif any(kw in desc_lower for kw in severity_keywords):
        for kw in severity_keywords:
            if kw in desc_lower:
                reason = f"Contains severity keyword '{kw}'"
                break
    
    # Ambiguity Flag
    flag = ""
    if category == "Other" and not any(kw in desc_lower for kw in severity_keywords):
        flag = "NEEDS_REVIEW"

    return {
        'complaint_id': complaint_id,
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
                    classified = classify_complaint(row)
                    # Merge original row with classification results
                    # Remove original category/priority if they exist to avoid duplicates
                    row.pop('category', None)
                    row.pop('priority_flag', None)
                    row.update(classified)
                    results.append(row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    continue
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    if not results:
        print("No results to write.")
        return

    fieldnames = results[0].keys()
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
