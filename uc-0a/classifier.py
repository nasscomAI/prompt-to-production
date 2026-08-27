#!/usr/bin/env python3
"""
UC-0A: Complaint Classifier
Classifies citizen complaints into categories and priorities with enforcement rules.
"""

import csv
import argparse
import sys
from pathlib import Path


# Allowed categories - exact strings only
ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category mapping keywords
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole in road", "crater", "depression in road"],
    "Flooding": ["flood", "flooded", "waterlogged", "water logging", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "light", "lighting", "lamp", "dark"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "bins", "smell", "dumped"],
    "Noise": ["noise", "loud", "music", "sound", "disturbance"],
    "Road Damage": ["road", "crack", "sinking", "surface", "footpath", "tiles", "manhole", "cover missing"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "temperature"],
    "Drain Blockage": ["drain", "blocked", "blockage", "clogged"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint into category, priority, reason, and flag.
    
    Args:
        row (dict): Dictionary containing complaint fields
        
    Returns:
        dict: Classification results with complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")
    
    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Detect category
    category = "Other"
    category_matches = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                category_matches.append(cat)
                break
    
    # Handle multiple category matches
    if len(category_matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description does not match known complaint categories"
    elif len(category_matches) == 1:
        category = category_matches[0]
        flag = ""
    else:
        # Multiple categories - pick the first (most severe) but flag for review
        category = category_matches[0]
        flag = "NEEDS_REVIEW"
        reason = f"Multiple categories detected: {', '.join(category_matches)}"
    
    # Detect priority based on severity keywords
    severity_found = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            severity_found.append(keyword)
    
    if severity_found:
        priority = "Urgent"
    else:
        # Standard for infrastructure issues, Low for minor
        if category in ["Noise", "Waste"]:
            priority = "Standard"
        elif category == "Other":
            priority = "Low"
        else:
            priority = "Standard"
    
    # Generate reason - cite specific words from description
    if flag == "NEEDS_REVIEW" and len(category_matches) > 1:
        # Reason already set above
        pass
    elif flag == "NEEDS_REVIEW" and len(category_matches) == 0:
        # Reason already set above
        pass
    else:
        reason_parts = []
        
        # Find category evidence
        category_evidence = []
        if category in CATEGORY_KEYWORDS:
            for keyword in CATEGORY_KEYWORDS[category]:
                if keyword in description_lower:
                    # Find the actual text in original description
                    start_idx = description_lower.find(keyword)
                    end_idx = start_idx + len(keyword)
                    actual_text = description[start_idx:end_idx]
                    category_evidence.append(f'"{actual_text}"')
                    break
        
        if category_evidence:
            reason_parts.append(f"Contains {category_evidence[0]} indicating {category} category")
        else:
            reason_parts.append(f"Classified as {category}")
        
        # Add priority evidence
        if severity_found:
            severity_text = ', '.join([f'"{kw}"' for kw in severity_found[:2]])  # Limit to 2 for brevity
            reason_parts.append(f"contains severity keywords {severity_text} requiring Urgent priority")
        else:
            reason_parts.append(f"{priority} priority")
        
        reason = ". ".join(reason_parts) + "."
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, classifies all complaints, writes output CSV.
    
    Args:
        input_path (str): Path to input CSV file
        output_path (str): Path to output CSV file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If required columns are missing
    """
    # Validate input file exists
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Read input CSV
    results = []
    required_columns = ["complaint_id", "description"]
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate required columns
            if not reader.fieldnames:
                raise ValueError("Input CSV has no columns")
            
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Warning: Failed to classify row {row_num} ({row.get('complaint_id', 'unknown')}): {e}", 
                          file=sys.stderr)
                    # Continue processing other rows
                    continue
    
    except Exception as e:
        raise IOError(f"Error reading input file: {e}")
    
    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output CSV
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Successfully classified {len(results)} complaints")
        print(f"Output written to: {output_path}")
        
        # Print summary
        urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
        flagged_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
        print(f"Summary: {urgent_count} Urgent, {flagged_count} flagged for review")
        
    except Exception as e:
        raise IOError(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
