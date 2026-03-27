"""
UC-0A classifier.py — Complaint Classifier.
Implements the Complaint Classification Agent defined in agents.md
using the skills defined in skills.md.
"""
import argparse
import csv
import sys
import os
import re

# Allowed categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    """
    Takes a single complaint description and returns its classification.
    Enforces rules from agents.md.
    """
    if not description or not isinstance(description, str):
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Invalid or empty input description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # 1. Determine Priority
    priority = "Standard"
    found_severity_keywords = []
    for keyword in SEVERITY_KEYWORDS:
        # Use regex for word boundary to avoid partial matches
        if re.search(rf'\b{keyword}\b', desc_lower):
            found_severity_keywords.append(keyword)
            
    if found_severity_keywords:
        priority = "Urgent"

    # 2. Determine Category
    category = "Other"
    flag = ""
    matched_category_keywords = []
    
    # Simple keyword matching for categories
    if any(word in desc_lower for word in ["pothole", "crater", "hole in road"]):
        category = "Pothole"
        matched_category_keywords.extend([w for w in ["pothole", "crater", "hole in road"] if w in desc_lower])
    elif any(word in desc_lower for word in ["flood", "waterlogging", "water logging", "submerged"]):
        category = "Flooding"
        matched_category_keywords.extend([w for w in ["flood", "waterlogging", "water logging", "submerged"] if w in desc_lower])
    elif any(word in desc_lower for word in ["light", "dark", "lamp", "street light"]):
        category = "Streetlight"
        matched_category_keywords.extend([w for w in ["light", "dark", "lamp", "street light"] if w in desc_lower])
    elif any(word in desc_lower for word in ["waste", "garbage", "trash", "dump", "rubbish"]):
        category = "Waste"
        matched_category_keywords.extend([w for w in ["waste", "garbage", "trash", "dump", "rubbish"] if w in desc_lower])
    elif any(word in desc_lower for word in ["noise", "loud", "music", "speaker"]):
        category = "Noise"
        matched_category_keywords.extend([w for w in ["noise", "loud", "music", "speaker"] if w in desc_lower])
    elif any(word in desc_lower for word in ["road damage", "broken road", "crack"]):
        category = "Road Damage"
        matched_category_keywords.extend([w for w in ["road damage", "broken road", "crack"] if w in desc_lower])
    elif any(word in desc_lower for word in ["heritage", "monument", "statue", "historic"]):
        category = "Heritage Damage"
        matched_category_keywords.extend([w for w in ["heritage", "monument", "statue", "historic"] if w in desc_lower])
    elif any(word in desc_lower for word in ["heat", "sun", "temperature"]):
        category = "Heat Hazard"
        matched_category_keywords.extend([w for w in ["heat", "sun", "temperature"] if w in desc_lower])
    elif any(word in desc_lower for word in ["drain", "sewer", "clog", "block"]):
        category = "Drain Blockage"
        matched_category_keywords.extend([w for w in ["drain", "sewer", "clog", "block"] if w in desc_lower])
    else:
        # If category cannot be determined, flag it
        flag = "NEEDS_REVIEW"

    # 3. Construct Reason
    reason_parts = []
    if matched_category_keywords:
        reason_parts.append(f"Categorized as {category} due to words: {', '.join(set(matched_category_keywords))}.")
    else:
        reason_parts.append("Could not determine specific category from text.")
        
    if found_severity_keywords:
        reason_parts.append(f"Priority set to Urgent due to severity keywords: {', '.join(set(found_severity_keywords))}.")
    else:
        reason_parts.append("No severity keywords found, priority is Standard.")
        
    reason = " ".join(reason_parts)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    """
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    try:
        with open(input_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            if 'description' not in fieldnames:
                print("Error: Input CSV must contain a 'description' column.")
                sys.exit(1)
                
            # Prepare output fieldnames
            out_fieldnames = [f for f in fieldnames if f not in ['category', 'priority', 'reason', 'flag']]
            out_fieldnames.extend(['category', 'priority', 'reason', 'flag'])
            
            rows = list(reader)

        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            
            for row in rows:
                description = row.get('description', '')
                classification = classify_complaint(description)
                
                # Update row with classification results
                row.update(classification)
                writer.writerow(row)
                
        print(f"Successfully processed {len(rows)} complaints. Results saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing files: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()
