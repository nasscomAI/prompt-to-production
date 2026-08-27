"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority enforcement
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    urgent_match = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            urgent_match = kw
            break
            
    # Category enforcement mapping
    category_mapping = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash", "dead animal", "dumped", "bin"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["cracked", "sinking", "broken", "manhole", "road surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "overflowing", "blocked"]
    }
    
    matched_categories = []
    category_match_word = None
    for cat, keywords in category_mapping.items():
        for kw in keywords:
            if kw in description:
                matched_categories.append(cat)
                if category_match_word is None:
                    category_match_word = kw
    
    # Remove duplicates
    matched_categories = list(set(matched_categories))
    
    flag = ""
    # Reason enforcement
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason = f"Classified as {category} based on presence of the word '{category_match_word}' in description."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Category is ambiguous due to multiple conflicting keywords found in description."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not determine a specific category from the description alone."
        
    if priority == "Urgent":
        reason += f" Priority set to Urgent because description cites '{urgent_match}'."
        
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
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV lacks header row")
                
            fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    row.update(result)
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    row['flag'] = 'ERROR'
                    writer.writerow(row)
                    
    except Exception as e:
        print(f"Failed to process batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
