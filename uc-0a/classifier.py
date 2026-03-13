"""
UC-0A — Complaint Classifier
Built using AI tool + RICE prompt guidelines.
"""
import argparse
import csv
import sys

# Allowed taxonomy from RICE enforcement
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords for Priority = Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "Categorized based on general observation."
    flag = ""
    
    # 1. Evaluate Priority based on severity keywords
    urgent_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    if urgent_words:
        priority = "Urgent"
    
    # 2. Evaluate Category (simulated strict NLP extraction)
    if "pothole" in desc or "tyre damage" in desc:
        category = "Pothole"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
        if "drain" in desc and "block" in desc:
            category = "Drain Blockage"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "animal" in desc or "trash" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc or "loud" in desc:
        category = "Noise"
    elif "road" in desc and ("crack" in desc or "sink" in desc):
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    elif "drain" in desc or "blockage" in desc:
        category = "Drain Blockage"
    elif "manhole" in desc or "tile" in desc or "footpath" in desc:
        category = "Road Damage"

    # 3. Formulate Reason (cite specific words)
    # Using the exact word driving the classification if possible
    key_phrases = []
    if urgent_words:
        key_phrases.append(f"severity keyword '{urgent_words[0]}'")
    
    cat_hints = {
        "Pothole": "pothole", "Flooding": "flood", "Streetlight": "light",
        "Waste": "waste/garbage/animal", "Noise": "noise/music",
        "Road Damage": "crack/sink/footpath", "Drain Blockage": "drain blocked",
        "Heritage Damage": "heritage", "Heat Hazard": "heat"
    }
    hint = cat_hints.get(category, "general description")
    if hint in desc or "/" in hint:  # Handle the multi-hints
        reason = f"The description mentions '{hint.split('/')[0] if '/' in hint else hint}', leading to the '{category}' classification."
    
    if urgent_words:
        reason += f" Mention of '{urgent_words[0]}' triggered the Urgent priority."

    # 4. Handle ambiguity (NEEDS_REVIEW flag)
    # If it's too short or doesn't map to anything but "Other"
    if category == "Other" and len(desc.split()) < 4:
        flag = "NEEDS_REVIEW"
        reason = "The description text is too ambiguous or brief to definitively categorize."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    results = []
    for row in rows:
        try:
            # Check for null row issues
            if not row.get('complaint_id') and not row.get('description'):
                continue # Skip completely empty rows
                
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            # Do not crash on bad rows
            print(f"Warning: Failed to process row ID {row.get('complaint_id', 'UNKNOWN')}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", "ERROR"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Processing error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            
    # Write output
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except IOError as e:
        print(f"Error: Could not write to output file '{output_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Classified {args.input} and wrote results to {args.output}")
