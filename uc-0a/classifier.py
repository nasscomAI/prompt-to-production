#!/usr/bin/env python3
"""
UC-0A: Complaint Classifier
Classifies civic complaints by category and priority.
"""

import csv
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional

# Fixed taxonomy
CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

# Category detection patterns
CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "hole", "crater", "pit", "bump"],
    "Flooding": ["flood", "water", "drain", "overflow", "sewage backup"],
    "Streetlight": ["light", "lamp", "street light", "lighting", "dark", "bulb"],
    "Waste": ["waste", "garbage", "trash", "debris", "litter", "rubbish"],
    "Noise": ["noise", "sound", "loud", "horn", "honking", "music"],
    "Road Damage": ["road damage", "pothole", "pavement", "cracked", "broken"],
    "Heritage Damage": ["heritage", "historic", "monument", "temple", "statue"],
    "Heat Hazard": ["heat", "hot", "temperature", "summer"],
    "Drain Blockage": ["drain", "blockage", "clogged", "blocked"],
}

def extract_phrase(description: str, category: str) -> str:
    """Extract justifying phrase from description."""
    desc_lower = description.lower()
    patterns = CATEGORY_PATTERNS.get(category, [])
    
    for pattern in patterns:
        if pattern in desc_lower:
            idx = desc_lower.find(pattern)
            start = max(0, idx - 10)
            end = min(len(description), idx + len(pattern) + 20)
            return description[start:end].strip()
    
    words = description.split()[:15]
    return " ".join(words)

def classify_complaint(complaint_id: str, description: str) -> Dict[str, str]:
    """Classify a single complaint."""
    
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Insufficient detail in complaint.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc = description.strip()
    desc_lower = desc.lower()
    
    # Check severity keywords
    priority = "Urgent" if any(kw in desc_lower for kw in SEVERITY_KEYWORDS) else "Standard"
    
    # Match categories
    matches = []
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(p in desc_lower for p in patterns):
            matches.append(category)
    
    if len(matches) == 1:
        category = matches[0]
        flag = ""
    elif len(matches) > 1:
        category = matches[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    phrase = extract_phrase(desc, category)
    reason = f"Contains '{phrase}' — classified as {category}."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file: str, output_file: str) -> None:
    """Read input CSV, classify rows, write output CSV."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                print("Error: Input CSV must have 'description' column", file=sys.stderr)
                sys.exit(1)
            
            for row_num, row in enumerate(reader, start=2):
                if all(not v.strip() for v in row.values()):
                    continue
                
                try:
                    complaint_id = row.get('id', '').strip() or f"row_{row_num}"
                    description = row.get('description', '').strip()
                    
                    result = classify_complaint(complaint_id, description)
                    result['id'] = complaint_id
                    result['description'] = description
                    
                    for key, value in row.items():
                        if key not in result:
                            result[key] = value.strip() if isinstance(value, str) else value
                    
                    results.append(result)
                
                except Exception as e:
                    result = {
                        'id': row.get('id', f'row_{row_num}'),
                        'description': row.get('description', ''),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': 'Classification error.',
                        'flag': 'NEEDS_REVIEW'
                    }
                    results.append(result)
    
    except Exception as e:
        print(f"Error reading CSV: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if not results:
            print("Warning: No rows to classify", file=sys.stderr)
            return
        
        fieldnames = ['id', 'description', 'category', 'priority', 'reason', 'flag']
        all_keys = set()
        for row in results:
            all_keys.update(row.keys())
        
        for key in all_keys:
            if key not in fieldnames:
                fieldnames.append(key)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({k: row.get(k, '') for k in fieldnames})
        
        print(f"Classified {len(results)} complaints → {output_file}")
    
    except Exception as e:
        print(f"Error writing CSV: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Classify civic complaints")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()