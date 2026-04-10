"""
UC-0A — Complaint Classifier
Implementation based on R.I.C.E framework, agents.md, and skills.md.
"""
import argparse
import csv
import re
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to the R.I.C.E rules.
    """
    description = row.get('description', '').strip()
    desc_lower = description.lower()
    complaint_id = row.get('complaint_id', 'Unknown')

    # 1. Category Mapping (Strict Taxonomy Enforcement)
    category = "Other"
    priority = "Standard"
    flag = ""
    
    # Mapping keywords to specific categories
    categories_keywords = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlogged", "inundated", "knee-deep", "rain"],
        "Streetlight": ["streetlight", "street light", "lamp", "dark", "flickering"],
        "Waste": ["garbage", "waste", "trash", "bin", "animal", "dumped"],
        "Noise": ["noise", "music", "loud", "sound"],
        "Road Damage": ["road surface", "cracked", "sinking", "manhole", "footpath", "tiles", "broken"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "temperature", "sun"],
        "Drain Blockage": ["drain", "sewage", "gutter", "block"]
    }

    # Identify matching categories
    matches = []
    for cat, keywords in categories_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                matches.append((cat, kw))
                break # Only need one keyword match per category

    if not matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len({m[0] for m in matches}) == 1:
        category = matches[0][0]
    else:
        # Heuristic for multiple matches
        unique_cats = {m[0] for m in matches}
        if "Drain Blockage" in unique_cats:
            category = "Drain Blockage"
        elif "Heritage Damage" in unique_cats:
            category = "Heritage Damage"
        elif "Pothole" in unique_cats:
            category = "Pothole"
        else:
            category = matches[0][0]
        # Ambiguity flag if multiple distinct categories are found
        if len(unique_cats) > 1:
            flag = "NEEDS_REVIEW"

    # 2. Priority Logic (Severity Rule Enforcement)
    # Urgent keywords strictly from R.I.C.E enforcement rules
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(kw in desc_lower for kw in urgent_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    # 3. Reason Generation (Cite specific words)
    # Extract the matched keyword or significant nouns/adjectives
    trigger_words = [m[1] for m in matches] if matches else ["description text"]
    # Ensure reason is a single sentence
    reason = f"Classified as {category} because the description mentions {', '.join(trigger_words[:2])}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Process input CSV and write classification results to output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Basic validation of input columns
            if 'description' not in reader.fieldnames:
                print(f"Error: Input CSV {input_path} missing 'description' column.")
                return
            
            for row in reader:
                results.append(classify_complaint(row))
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    # Define the required output schema
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Batch classification complete. Results saved to: {args.output}")
