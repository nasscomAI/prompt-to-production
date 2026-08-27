#!/usr/bin/env python3
"""
UC-0A: Complaint Classifier
Classifies citizen complaints with strict taxonomy and severity enforcement.
"""

import csv
import argparse
import sys
from pathlib import Path


# Allowed categories - exact strings only
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(complaint_id, description):
    """
    Classify a single complaint into category and priority.
    
    Args:
        complaint_id: Unique identifier for the complaint
        description: Text description of the complaint
    
    Returns:
        dict with keys: complaint_id, category, priority, reason, flag
    """
    description_lower = description.lower()
    
    # Initialize result
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": ""
    }
    
    # Category classification with keyword matching
    category_keywords = {
        "Pothole": ["pothole", "tyre damage", "road hole", "hole"],
        "Flooding": ["flood", "waterlogged", "water", "rain", "stranded", "knee-deep"],
        "Streetlight": ["streetlight", "light", "dark", "lamp", "flickering", "sparking"],
        "Waste": ["garbage", "waste", "smell", "bins", "overflowing", "animal"],
        "Noise": ["noise", "music", "loud", "midnight"],
        "Road Damage": ["road", "crack", "surface", "manhole", "sinking", "tiles", "footpath"],
        "Heritage Damage": ["heritage"],
        "Drain Blockage": ["drain", "blocked"]
    }
    
    matched_categories = []
    matched_keywords = []
    
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in description_lower:
                matched_categories.append(category)
                matched_keywords.append(keyword)
                break
    
    # Handle category assignment
    if len(matched_categories) == 1:
        result["category"] = matched_categories[0]
        category_reason = f"'{matched_keywords[0]}'"
    elif len(matched_categories) > 1:
        # Multiple matches - use first but flag for review
        result["category"] = matched_categories[0]
        result["flag"] = "NEEDS_REVIEW"
        category_reason = f"'{matched_keywords[0]}' (multiple categories possible)"
    else:
        # No match - use Other and flag
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
        category_reason = "no clear category match"
    
    # Priority classification - check for severity keywords
    severity_found = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            severity_found.append(keyword)
    
    if severity_found:
        result["priority"] = "Urgent"
        priority_reason = f"severity keyword '{severity_found[0]}'"
    else:
        # Determine Standard vs Low
        if result["category"] in ["Pothole", "Flooding", "Road Damage", "Drain Blockage"]:
            result["priority"] = "Standard"
            priority_reason = "infrastructure issue"
        elif result["category"] == "Noise":
            result["priority"] = "Low"
            priority_reason = "minor inconvenience"
        else:
            result["priority"] = "Standard"
            priority_reason = "standard issue"
    
    # Build reason string
    result["reason"] = f"Description contains {category_reason} indicating {result['category']} category"
    if severity_found:
        result["reason"] += f" and {priority_reason} indicating {result['priority']} priority"
    
    return result


def batch_classify(input_file, output_file):
    """
    Read complaints from CSV, classify each, and write results.
    
    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
    """
    # Validate input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    results = []
    
    # Read and process input
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                complaint_id = row['complaint_id']
                description = row['description']
                
                # Classify the complaint
                result = classify_complaint(complaint_id, description)
                results.append(result)
        
        print(f"Processed {len(results)} complaints")
        
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write results
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Results written to {output_file}")
        
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Classify citizen complaints')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)


if __name__ == '__main__':
    main()
