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
    
    # Priority keywords from agents.md
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_urgent = [kw for kw in urgent_keywords if kw in description]
    
    if matched_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Category lists from agents.md
    categories = {
        "Pothole": ["pothole", "manhole"],
        "Flooding": ["flood", "rain", "water", "drainage"],
        "Streetlight": ["streetlight", "lights out", "dark at night", "dark"],
        "Waste": ["garbage", "waste", "dead animal", "smell", "dump"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["road surface", "crack", "sinking", "footpath", "tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "drain overflowing", "drain"]
    }
    
    matched_categories = []
    matched_cat_words = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_cat_words.append(kw)
                
    flag = ""
    reason = ""
    
    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description lacks clear keywords to confidently determine a category."
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous category match with keywords '{matched_cat_words[0]}' and '{matched_cat_words[1]}'."
    else:
        category = matched_categories[0]
        root_word = matched_cat_words[0]
        if matched_urgent:
            reason = f"Classified as {category} with Urgent priority due to mentioning '{root_word}' and '{matched_urgent[0]}'."
        else:
            reason = f"Classified as {category} because the description mentions '{root_word}'."
            
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                # Fallback error handling for robust processing
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Failed to parse row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
