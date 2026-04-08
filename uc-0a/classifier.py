"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
from typing import Dict, List

# Allowed categories as per agents.md enforcement rules
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority (from agents.md)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Category keywords mapping for classification logic
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "hole in road", "crater", "depression in road"],
    "Flooding": ["flood", "water logging", "waterlogged", "overflow", "inundation", "submerg"],
    "Streetlight": ["streetlight", "street light", "lamp", "lighting", "dark", "illumination"],
    "Waste": ["garbage", "trash", "waste", "litter", "rubbish", "dump"],
    "Noise": ["noise", "loud", "sound", "disturbance", "pollution"],
    "Road Damage": ["road damage", "crack", "broken road", "pavement", "surface"],
    "Heritage Damage": ["heritage", "monument", "historic", "archaeological", "ancient"],
    "Heat Hazard": ["heat", "hot", "temperature", "heatwave", "sun exposure"],
    "Drain Blockage": ["drain", "sewer", "clog", "blockage", "blocked drain", "drainage"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agents.md enforcement rules.
    
    Args:
        row: dict with at minimum a 'description' field
        
    Returns: 
        dict with keys: category, priority, reason, flag
    """
    description = row.get('description', '').strip()
    
    # Error handling: missing or empty description
    if not description:
        return {
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided',
            'flag': 'NEEDS_REVIEW'
        }
    
    description_lower = description.lower()
    
    # Classify category based on keyword matching
    category = 'Other'
    matched_keywords = []
    confidence_scores = {}
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in description_lower]
        if matches:
            confidence_scores[cat] = len(matches)
            if len(matches) > len(matched_keywords):
                category = cat
                matched_keywords = matches
    
    # Determine priority based on urgent keywords
    urgent_found = [kw for kw in URGENT_KEYWORDS if kw in description_lower]
    if urgent_found:
        priority = 'Urgent'
    elif category != 'Other' and matched_keywords:
        priority = 'Standard'
    else:
        priority = 'Low'
    
    # Generate reason citing specific words from description
    if matched_keywords:
        cited_words = ', '.join([f'"{kw}"' for kw in matched_keywords[:3]])
        reason = f'Description contains {cited_words} indicating {category} issue.'
    elif urgent_found:
        cited_words = ', '.join([f'"{kw}"' for kw in urgent_found[:2]])
        reason = f'Description contains urgent keywords {cited_words}.'
    else:
        reason = 'Unable to confidently determine category from description.'
    
    # Set flag for ambiguous cases
    flag = ''
    if category == 'Other' and not matched_keywords:
        flag = 'NEEDS_REVIEW'
    elif len(confidence_scores) > 1:
        # Multiple categories matched - check if it's ambiguous
        sorted_scores = sorted(confidence_scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] == sorted_scores[1]:
            flag = 'NEEDS_REVIEW'
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Implements error handling as per skills.md specifications.
    
    Args:
        input_path: Path to input CSV with complaint descriptions
        output_path: Path to write results CSV
        
    Raises:
        FileNotFoundError: If input file does not exist or is not readable
        ValueError: If input CSV is malformed or missing required columns
        PermissionError: If output path is not writable
    """
    # Validate input file
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not os.access(input_path, os.R_OK):
        raise FileNotFoundError(f"Input file is not readable: {input_path}")
    
    # Validate output path is writable
    output_dir = os.path.dirname(output_path) or '.'
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Output directory is not writable: {output_dir}")
    
    # Read input CSV
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                raise ValueError("Input CSV is empty")
            
            # Check for description column
            if 'description' not in reader.fieldnames:
                raise ValueError("Input CSV missing required 'description' column")
            
            input_fieldnames = reader.fieldnames
    except csv.Error as e:
        raise ValueError(f"Input CSV is malformed: {e}")
    
    # Process all rows
    results = []
    for row in rows:
        classification = classify_complaint(row)
        
        # Merge original row with classification results
        result_row = {**row}
        result_row.update(classification)
        results.append(result_row)
    
    # Write output CSV
    output_fieldnames = list(input_fieldnames) + ['category', 'priority', 'reason', 'flag']
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
