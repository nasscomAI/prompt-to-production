"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with updated keys including category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "No definitive category found; needs review."
    flag = "NEEDS_REVIEW"

    if not desc.strip():
        reason = "Empty description; cannot determine category or priority."
        return {'category': category, 'priority': priority, 'reason': reason, 'flag': flag}

    # Priority keyword mapping
    urgent_kws = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_urgent = next((kw for kw in urgent_kws if kw in desc), None)
    if matched_urgent:
        priority = "Urgent"

    # Category keyword mapping
    cat_kws = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "submerge", "water"],
        "Streetlight": ["streetlight", "lights out", "streetlamp", "dark", "light"],
        "Waste": ["garbage", "waste", "trash", "dump", "animal", "smell"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["crack", "road surface", "broken", "manhole", "tiles"],
        "Heritage Damage": ["heritage", "monument", "historic"],
        "Heat Hazard": ["heat", "sunstroke", "temperature"],
        "Drain Blockage": ["drain", "clog", "sewer", "blockage"]
    }
    
    matched_cats = []
    matched_cat_word = None
    
    for c_name, kws in cat_kws.items():
        found = next((kw for kw in kws if kw in desc), None)
        if found:
            matched_cats.append(c_name)
            if not matched_cat_word: # save first match word to cite in reason
                matched_cat_word = found

    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = "" # Clear review flag as category is unambiguous
        
        if priority == "Urgent":
            reason = f"Description marked as '{category}' due to '{matched_cat_word}' and priority is Urgent because it mentions '{matched_urgent}'."
        else:
            reason = f"Complaint categorized as '{category}' based on the word '{matched_cat_word}'."
            
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if priority == "Urgent":
            reason = f"Description contains ambiguous categories ({', '.join(matched_cats)}) but priority is Urgent due to '{matched_urgent}'."
        else:
            reason = f"Description is ambiguous as it matches multiple categories ({', '.join(matched_cats)})."
            
    else: # 0 matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        if priority == "Urgent":
            reason = f"Priority is Urgent due to '{matched_urgent}' but category requires manual review."
        else:
            reason = "Category cannot be determined from description alone, requiring review."

    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames if reader.fieldnames else []
    except Exception as e:
        print(f"Error reading file {input_path}: {e}")
        return

    # Add new output fields based on schema
    out_fields = fieldnames + ['category', 'priority', 'reason', 'flag']
    
    results = []
    for i, row in enumerate(rows):
        if not row:
            continue
        try:
            classification = classify_complaint(row)
            row.update(classification)
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            row['category'] = 'Other'
            row['priority'] = 'Standard'
            row['reason'] = f'Exception processing row: {e}'
            row['flag'] = 'NEEDS_REVIEW'
        
        results.append(row)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
