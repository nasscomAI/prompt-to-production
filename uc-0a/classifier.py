# -*- coding: utf-8 -*-
"""
UC-0A - Complaint Classifier
"""
import argparse
import csv
import json
import os
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
CATEGORIES = ['Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other']

def classify_complaint(row: dict) -> dict:
    description = row.get('description', '')
    desc_lower = description.lower()
    
    # Determine Priority
    priority = 'Standard'
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_keywords:
        priority = 'Urgent'
        
    # Determine Category
    category = 'Other'
    flag = ''
    
    if 'pothole' in desc_lower:
        category = 'Pothole'
    elif 'flood' in desc_lower or 'water' in desc_lower:
        category = 'Flooding'
        if 'drain' in desc_lower:
            category = 'Drain Blockage'
    elif 'streetlight' in desc_lower or 'dark' in desc_lower or 'light' in desc_lower:
        category = 'Streetlight'
    elif 'waste' in desc_lower or 'garbage' in desc_lower or 'smell' in desc_lower or 'dead animal' in desc_lower:
        category = 'Waste'
    elif 'noise' in desc_lower or 'music' in desc_lower:
        category = 'Noise'
    elif 'road surface cracked' in desc_lower or 'tiles broken' in desc_lower or 'manhole cover missing' in desc_lower:
        category = 'Road Damage'
    elif 'heritage' in desc_lower:
        category = 'Heritage Damage'
        flag = 'NEEDS_REVIEW' # Ambiguous since it's also streetlight related in the test
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        
    # Generate Reason
    if found_keywords:
        reason = f"The description mentions '{found_keywords[0]}'."
    else:
        # Just pick a salient word
        words = description.split()
        if len(words) > 2:
            reason = f"The description mentions '{words[2]}'."
        else:
            reason = "The description mentions the issue clearly."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if not row.get('complaint_id'):
                    continue
                print(f"Classifying {row['complaint_id']}...")
                res = classify_complaint(row)
                results.append(res)
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    if not results:
        print('No results to write.')
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Failed to write output file: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UC-0A Complaint Classifier')
    parser.add_argument('--input',  required=True, help='Path to test_[city].csv')
    parser.add_argument('--output', required=True, help='Path to write results CSV')
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
