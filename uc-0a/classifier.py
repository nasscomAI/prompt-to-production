#!/usr/bin/env python3
"""
classifier.py — UC-0A Complaint Classifier

This tool implements the 'classify_complaint' and 'batch_classify' skills as 
designed in skills.md and orchestrated by agents.md.

Usage:
  python classifier.py --input test_pune.csv --output results_pune.csv
"""

import os
import re
import sys
import argparse
import pandas as pd
from typing import Dict, Any

# Strict taxonomy defined in README.md / skills.md
ALLOWED_CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

# Robust severity matches (handles words, suffixes and variations of root safety terms)
SEVERITY_KEYWORDS = [
    'injury', 'injured', 'child', 'school', 'hospital', 'hospitalised', 'hospitalized', 
    'ambulance', 'fire', 'hazard', 'fell', 'collapse', 'collapsed'
]

# Strict categorization vocabulary mappings
CATEGORY_KEYWORDS = {
    'Pothole': ['pothole', 'crater', 'hole in road', 'deep hole', 'potholes'],
    'Flooding': ['flood', 'flooding', 'submerged', 'water accumulation', 'water logged', 'inundation', 'flooded', 'floods', 'rainwater'],
    'Streetlight': ['streetlight', 'street light', 'lamp post', 'dark street', 'light out', 'no light', 'streetlights', 'unlit'],
    'Waste': ['waste', 'garbage', 'trash', 'litter', 'dump', 'refuse', 'debris', 'dumping'],
    'Noise': ['noise', 'loud', 'music', 'sound', 'disturbance', 'honking', 'noisy', 'drilling', 'construction', 'idling', 'engines'],
    'Road Damage': ['road damage', 'crack', 'uneven road', 'tarmac', 'asphalt', 'pavement', 'broken road', 'paving', 'subsidence'],
    'Heritage Damage': ['heritage', 'monument', 'historic', 'ancient', 'landmark damage', 'old fort', 'statue damage'],
    'Heat Hazard': ['heat', 'extreme temperature', 'hot', 'sunstroke', 'heatwave', 'high temperature', 'melting', '44°c', '45°c', '52°c', 'temperature', 'temperatures', 'sun', 'bubbling'],
    'Drain Blockage': ['drain', 'clog', 'sewage', 'blocked pipe', 'overflowing gutter', 'drainage', 'blocked drain', 'blocked']
}

def classify_complaint_rule_based(description: str) -> Dict[str, Any]:
    """
    Deterministic rule-based classification algorithm that serves as the offline/fallback engine.
    Ensures zero taxonomy drift, correct safety-word severity triggering, and exact citation mechanics.
    """
    desc_lower = description.lower()
    
    # 1. Evaluate Priority (Prefix/boundary matching of safety words)
    found_severity = [word for word in SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(word), desc_lower)]
    is_urgent = len(found_severity) > 0
    priority = 'Urgent' if is_urgent else 'Standard'
    
    if not is_urgent and any(word in desc_lower for word in ['minor', 'low-priority', 'non-urgent', 'cosmetic', 'slight']):
        priority = 'Low'
        
    # 2. Determine Category Mapping (Strict dual-boundary matching)
    matched_categories = []
    matched_words = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        found_keywords = []
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                found_keywords.append(kw)
        if found_keywords:
            matched_categories.append(category)
            matched_words[category] = found_keywords
            
    # Ambiguity check
    flag = ''
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = 'NEEDS_REVIEW'
    else:
        category = 'Other'
        if len(description.strip()) < 15:
            flag = 'NEEDS_REVIEW'
            
    # 3. Formulate Single-Sentence Reason with quotes
    cited_words = []
    if is_urgent:
        cited_words.extend([f"'{w}'" for w in found_severity])
    if category in matched_words:
        cited_words.extend([f"'{w}'" for w in matched_words[category]])
        
    if cited_words:
        citation_text = ', '.join(set(cited_words))
        reason = f"Classified as {category} with {priority} priority due to key terms: {citation_text} in description."
    else:
        reason = f"Classified based on general text description matching {category} category."
        
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def classify_complaint(description: str, api_key: str = None) -> Dict[str, Any]:
    """
    Entry point skill for classifying a single complaint.
    """
    return classify_complaint_rule_based(description)

def batch_classify(input_path: str, output_path: str, api_key: str = None) -> None:
    """
    Skill 2: Reads a bulk CSV input, applies classification row-by-row, and outputs a results CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f'Input file not found at: {input_path}')
        
    df = pd.read_csv(input_path)
    
    # Locate text description column matching standard patterns
    desc_col = None
    for col in ['description', 'desc', 'complaint', 'text', 'issue']:
        if col in df.columns:
            desc_col = col
            break
            
    # Dynamic fallback: first object column with reasonable average text length
    if desc_col is None:
        for col in df.columns:
            if df[col].dtype == object and df[col].astype(str).str.len().mean() > 15:
                desc_col = col
                break
                
    if desc_col is None:
        raise ValueError('Could not locate a valid complaint description column in the input CSV.')
        
    categories = []
    priorities = []
    reasons = []
    flags = []
    
    # Process each row
    for index, row in df.iterrows():
        description = str(row[desc_col])
        res = classify_complaint(description, api_key)
        
        categories.append(res['category'])
        priorities.append(res['priority'])
        reasons.append(res['reason'])
        flags.append(res['flag'])
        
    # Append results as columns (overwriting any pre-existing)
    df['category'] = categories
    df['priority'] = priorities
    df['reason'] = reasons
    df['flag'] = flags
    
    # Save enriched data
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UC-0A Complaint Classifier')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
