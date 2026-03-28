"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with updated keys: category, priority, reason, flag
    """
    description = row.get("description", "")
    if not description:
        description = row.get("text", "")
    
    desc_lower = description.lower()
    
    # Rule 1: Category must be mapped to exactly one of the valid outputs natively, including synonyms
    category_synonyms = {
        "Pothole": ["pothole", "potholes", "crater", "craters"],
        "Flooding": ["flooding", "flooded", "flood", "floods", "waterlog", "waterlogged", "waterlogging", "submerged"],
        "Streetlight": ["streetlight", "streetlights", "street light", "street lights", "street lamp", "street lamps", "broken light", "lights out", "light out", "lights not working", "dark street", "Darkness"],
        "Waste": ["waste", "wastes", "garbage", "trash", "rubbish", "litter", "dump", "dumping", "dumped"],
        "Noise": ["noise", "noisy", "loud", "blaring", "honking", "disturbance", "music", "loud music", "band playing"],
        "Road Damage": ["road damage", "broken road", "cracked road", "damaged road", "uneven road", "road surface cracked"],
        "Heat Hazard": ["heat hazard", "heatwave", "extreme heat", "excessive heat", "high temperature", "dangerous temperatures", "°c"],
        "Drain Blockage": ["drain blockage", "blocked drain", "clogged drain", "drain", "drains", "sewer", "sewers", "clogged", "overflowing drain", "draining"],
        "Heritage Damage": ["heritage damage", "heritage", "monument", "statue", "historical"]
    }
    
    category = "Other"
    cited_cat = None
    
    for official_cat, synonyms in category_synonyms.items():
        for syn in synonyms:
            # Handle standard words with boundary limits, but allow raw matching for degree symbols
            if "°" in syn:
                pattern = syn.replace(' ', r'\s+')
            else:
                pattern = r'\b' + syn.replace(' ', r'\s+') + r'\b'
                
            if re.search(pattern, desc_lower):
                category = official_cat
                cited_cat = syn
                break
        if category != "Other":
            break
            
    # Rule 2/3: Priority must be one of Urgent, Standard, Low and mapped to Urgent if keywords present
    severity_keywords = [
        "injury", "child", "school", "hospital", "hospitalised", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    low_keywords = ["minor", "small", "slight"]
    
    priority = "Standard" # Must be one of Urgent, Standard, Low
    cited_sev = None
    
    # Check for Urgent first (highest priority)
    for word in severity_keywords:
        if re.search(r'\b' + word + r'\b', desc_lower):
            priority = "Urgent"
            cited_sev = word
            break
            
    # If not Urgent, check for Low
    if priority == "Standard":
        for word in low_keywords:
            if re.search(r'\b' + word + r'\b', desc_lower):
                priority = "Low"
                cited_sev = word
                break
            
    # Rule 4: Every output row must include a reason field consisting of exactly one sentence citing specific words
    if cited_sev and priority == "Urgent":
        reason = f"The priority is Urgent because the description mentions the severity keyword '{cited_sev}'."
    elif cited_sev and priority == "Low":
        reason = f"The priority is Low because the description mentions the indicator keyword '{cited_sev}'."
    elif cited_cat:
        reason = f"The issue is '{category}' because the description includes the word '{cited_cat}'."
    else:
        reason = "No matching keywords were found in the description."
        
    # Rule 5: Ambiguous cases set to Other with flag NEEDS_REVIEW
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # Returning updated row
    row["category"] = category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = list(reader.fieldnames)
    except Exception as e:
        print(f"Error opening input file: {e}")
        return

    # Fill mapping properties natively
    for f in ["category", "priority", "reason", "flag"]:
        if f not in fieldnames:
            fieldnames.append(f)

    # Process each row
    for i, row in enumerate(rows):
        try:
            rows[i] = classify_complaint(row)
        except Exception as e:
            # Handle malformed/unprocessable row elegantly
            print(f"Row {i} is malformed or unprocessable. Logging failure: {e}")
            row["category"] = "Other"
            row["priority"] = "Standard"
            row["reason"] = "Failed to process row due to exception."
            row["flag"] = "NEEDS_REVIEW"
            rows[i] = row

    # Generate output completely
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
