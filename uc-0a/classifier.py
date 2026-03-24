"""
Municipal Complaint Classifier (UC-0A)

Implements complaint classification as specified in skills.md and agents.md.
Processes CSV files containing municipal complaint descriptions and assigns standardized
categories, priority levels, and justifications.
"""

import csv
import argparse
import sys
from typing import Dict, Optional
from pathlib import Path


# Valid categories as per enforcement rules
VALID_CATEGORIES = {
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
}

# Keywords that trigger 'Urgent' priority
URGENT_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
}

# Category keywords mapping for classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "crater", "hole in road", "uneven road", "broken road surface"],
    "Flooding": ["flood", "water", "inundated", "submerged", "waterlogged", "overflow", "drain"],
    "Streetlight": ["light", "lamp", "street light", "darkness", "broken light", "light not working", "bulb"],
    "Waste": ["waste", "garbage", "trash", "litter", "debris", "dumping", "rubbish", "junk"],
    "Noise": ["noise", "sound", "loud", "honking", "construction", "music", "noise pollution"],
    "Road Damage": ["road damage", "crack", "damaged road", "pavement", "asphalt", "surface damage"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "cultural", "archaeological"],
    "Heat Hazard": ["heat", "temperature", "hot", "extreme heat", "heat wave", "sun exposure"],
    "Drain Blockage": ["drain", "blocked", "clogged", "blockage", "sewage", "water drain", "overflow"]
}


def classify_complaint(row: Dict) -> Dict:
    """
    Analyzes a single complaint description to assign a standardized category,
    priority level, and justification.
    
    Args:
        row: A dictionary or row containing a 'description' string.
    
    Returns:
        A dictionary containing:
        - 'category': string (one of VALID_CATEGORIES)
        - 'priority': string ('Urgent' or 'Normal')
        - 'reason': string (one sentence citing specific words from description)
        - 'flag': string (empty or 'NEEDS_REVIEW')
    
    Error handling:
        If the description is empty or null, returns:
        - category: 'Other'
        - priority: 'Low'
        - flag: 'NEEDS_REVIEW'
    """
    
    # Extract description from row
    description = row.get('description', '') if isinstance(row, dict) else str(row)
    description = description.strip() if description else ""
    
    # Handle empty or null descriptions
    if not description:
        return {
            'category': 'Other',
            'priority': 'Low',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Convert to lowercase for keyword matching
    description_lower = description.lower()
    
    # Determine priority based on urgent keywords
    priority = 'Urgent' if any(keyword in description_lower for keyword in URGENT_KEYWORDS) else 'Normal'
    
    # Classify category based on keyword matching
    category = 'Other'
    matched_keywords = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                category = cat
                matched_keywords.append(keyword)
                break
        if category != 'Other':
            break
    
    # Generate reason sentence citing specific words from description
    if matched_keywords:
        keyword_str = f'"{matched_keywords[0]}"' if len(matched_keywords) == 1 else \
                      f'"{matched_keywords[0]}" and other relevant terms'
        reason = f'The description contains the keyword {keyword_str} which indicates {category.lower()}.'
    else:
        reason = f'Classification assigned based on description content analysis.'
    
    # Set flag for ambiguous classifications
    flag = 'NEEDS_REVIEW' if category == 'Other' else ''
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Orchestrates the end-to-end processing of a municipal CSV file,
    ensuring structural integrity of the output.
    
    Args:
        input_path: Path to input CSV file containing complaints
        output_path: Path to output CSV file where results will be written
    
    Error handling:
        - Validates that the input file exists
        - If a specific row fails classification, logs the error and continues
        - Ensures partial completion even if some rows fail
    
    Output columns:
        - description: original complaint description
        - category: standardized category
        - priority: Urgent or Normal
        - reason: justification sentence
        - flag: NEEDS_REVIEW or empty
    """
    
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    # Validate input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                raise ValueError("Input CSV must contain a 'description' column")
            
            # Write output header
            output_fieldnames = ['description', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    classification = classify_complaint(row)
                    
                    # Build output row
                    output_row = {
                        'description': row.get('description', ''),
                        'category': classification['category'],
                        'priority': classification['priority'],
                        'reason': classification['reason'],
                        'flag': classification['flag']
                    }
                    
                    writer.writerow(output_row)
                
                except Exception as e:
                    # Log error but continue processing
                    print(f"Warning: Error processing row {row_num}: {str(e)}", file=sys.stderr)
                    continue
        
        print(f"Done. Results written to {output_path}")
    
    except Exception as e:
        print(f"Error processing file: {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
