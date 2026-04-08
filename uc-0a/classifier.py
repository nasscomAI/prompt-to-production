"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os
import re

# Allowed categories and severity keywords as per README.md and agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def find_exact_keywords(text: str, keywords: list) -> list:
    """Helper to find keywords as whole words or specific symbols in text."""
    found = []
    for kw in keywords:
        # Match as whole word or specific patterns like °C
        if kw == "°c":
            pattern = re.escape(kw)
        else:
            # Match word with optional 's' or 'es' plural
            pattern = rf"\b{re.escape(kw)}(?:s|es)?\b"
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found.append(match.group())
    return found

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint based on description.
    Uses rules defined in agents.md.
    """
    description = row.get("description", "")
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description makes classification impossible.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority logic - strict triggers from agents.md
    priority = "Standard"
    triggered_priority = find_exact_keywords(description, SEVERITY_KEYWORDS)
    if triggered_priority:
        priority = "Urgent"
    
    # Category logic
    category = "Other"
    
    # Check for Heritage Damage first (High specificity)
    if re.search(r"\bheritage\b", desc_lower):
        category = "Heritage Damage"
    
    # Heat Hazard
    elif find_exact_keywords(description, ["heat", "hot", "temperature", "°c", "sun", "burn", "melting", "heatwave"]):
        category = "Heat Hazard"
        
    # Drain Blockage vs Flooding
    elif re.search(r"\bdrain\b", desc_lower):
        category = "Drain Blockage"
    elif re.search(r"\b(flood|water)\b", desc_lower):
        category = "Flooding"
        
    # Pothole
    elif re.search(r"\bpothole\b", desc_lower):
        category = "Pothole"
        
    # Streetlight
    elif re.search(r"\b(streetlight|lights?)\b", desc_lower):
        category = "Streetlight"
        
    # Noise
    elif re.search(r"\b(noise|music|loud|sound)\b", desc_lower):
        category = "Noise"
        
    # Waste
    elif find_exact_keywords(description, ["garbage", "waste", "animal", "bins", "manure", "rubbish", "refuse", "dumped"]):
        category = "Waste"
        
    # Road Damage
    elif find_exact_keywords(description, ["road", "cracked", "sinking", "footpath", "manhole", "tiles", "subsidence", "paving", "surface"]):
        category = "Road Damage"
        
    # Flag and Reason
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Keywords for reason evidence citation
    category_keywords_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "light", "lights"],
        "Waste": ["garbage", "waste", "animal", "bins", "rubbish", "dumped"],
        "Noise": ["noise", "music", "loud", "sound"],
        "Road Damage": ["road", "cracked", "sinking", "footpath", "manhole", "tiles", "subsidence", "paving", "surface"],
        "Heat Hazard": ["heat", "hot", "temperature", "°c", "sun", "burn", "melting", "heatwave"],
        "Heritage Damage": ["heritage"],
        "Drain Blockage": ["drain"]
    }
    
    found_cat_keywords = find_exact_keywords(description, category_keywords_map.get(category, []))

    # Single-sentence reason citing exact evidence
    if priority == "Urgent":
        reason = f"Classified as {category} and set to Urgent due to evidence keywords '{', '.join(set(triggered_priority))}'."
    elif found_cat_keywords:
        reason = f"Classified as {category} based on description keywords like '{', '.join(set(found_cat_keywords))}'."
    else:
        reason = f"Classified as {category} based on the overall description."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            original_fields = reader.fieldnames
            new_fields = ["category", "priority", "reason", "flag"]
            all_fields = original_fields + [f for f in new_fields if f not in original_fields]
            
            for row in reader:
                classification = classify_complaint(row)
                row.update(classification)
                results.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fields)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An error occurred during processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
