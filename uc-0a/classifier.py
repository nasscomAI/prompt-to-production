"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # 1. Determine priority using severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    matched_severity = []
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_severity.append(kw)
            
    # 2. Determine category indicators
    categories_indicators = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlog"],
        "Streetlight": ["streetlight", "unlit", "darkness", "lights out"],
        "Waste": ["garbage", "waste", "trash", "dead animal"],
        "Noise": ["music", "noise", "drilling", "amplifier", "wedding band"],
        "Road Damage": ["road surface", "cracked and sinking", "subsidence", "collapsed", "manhole cover", "footpath tiles", "broken bench", "upturned paving", "tarmac surface", "road dividers", "paving"],
        "Heritage Damage": ["heritage", "historic", "ancient"],
        "Heat Hazard": ["melting", "temperature", "heatwave", "bubbling", "burns", "sun"],
        "Drain Blockage": ["drain", "drains", "drainage"]
    }
    
    matched_categories = []
    for cat, indicators in categories_indicators.items():
        for ind in indicators:
            if ind in desc_lower:
                matched_categories.append(cat)
                break
                
    # Remove duplicates from matched categories
    matched_categories = list(set(matched_categories))
    
    # Check ambiguity
    flag = ""
    category = "Other"
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Genuinely ambiguous cases.
        flag = "NEEDS_REVIEW"
        # Hierarchy/Preference rules
        if "Heritage Damage" in matched_categories:
            category = "Heritage Damage"
        elif "Drain Blockage" in matched_categories:
            category = "Drain Blockage"
        elif "Flooding" in matched_categories:
            category = "Flooding"
        else:
            category = matched_categories[0]
    else:
        # Default or fallback
        if "broken" in desc_lower or "structural" in desc_lower:
            category = "Road Damage"
        else:
            category = "Other"
            
    # Make sure category is valid
    allowed_categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    if category not in allowed_categories:
        category = "Other"
        
    # Reason sentence: single sentence citing specific words from description
    cited_words = []
    for cat, indicators in categories_indicators.items():
        if cat == category:
            for ind in indicators:
                if ind in desc_lower:
                    start_idx = desc_lower.find(ind)
                    if start_idx != -1:
                        cited_words.append(f'"{description[start_idx:start_idx+len(ind)]}"')
                        
    if priority == "Urgent":
        for kw in matched_severity:
            start_idx = desc_lower.find(kw)
            if start_idx != -1:
                cited_words.append(f'"{description[start_idx:start_idx+len(kw)]}"')
                
    # Unique cited words list
    cited_words = list(dict.fromkeys(cited_words))
    
    if cited_words:
        reason = f"Classified as {category} with {priority} priority citing words {', '.join(cited_words)} from description."
    else:
        reason = f"Classified as {category} with {priority} priority."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file does not exist at {input_path}")
        return
        
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        # Check if reader has headers
        if not reader.fieldnames:
            print("Error: Input CSV is empty or has no headers")
            return
            
        for line_num, row in enumerate(reader, start=2):
            try:
                # Handle nulls / missing data safely
                if not row or all(not v for v in row.values()):
                    # empty line, skip or flag
                    continue
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Don't crash on bad rows, produce output even if some rows fail
                print(f"Warning: Failed to classify row on line {line_num}: {e}")
                # We can append a fallback result for the bad row if it has complaint_id
                c_id = row.get("complaint_id", f"UNKNOWN_{line_num}") if row else f"UNKNOWN_{line_num}"
                results.append({
                    "complaint_id": c_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Write to output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
