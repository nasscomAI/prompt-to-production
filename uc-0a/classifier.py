import argparse
import csv
import sys

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["garbage", "waste", "animal", "smell", "trash"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface", "footpath", "crack", "tiles", "sinking"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain", "manhole"]
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Identify matched categories
    matched_categories = []
    matched_cat_words = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_cat_words.append(kw)
                
    # Determine base category and flag
    category = "Other"
    flag = ""
    reason_cat_part = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        # Just cite the first word that matched for this category
        cited_word = [w for w in matched_cat_words if w in CATEGORY_KEYWORDS[category]][0]
        reason_cat_part = f"based on the word '{cited_word}'"
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat_part = f"due to ambiguous keywords ({', '.join(set(matched_cat_words))})"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat_part = "as no defined category keywords were found"
        
    # Identify priority based on severity keywords
    priority = "Standard" # Default
    matched_sev_words = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            matched_sev_words.append(kw)
            
    reason_sev_part = ""
    if priority == "Urgent":
        reason_sev_part = f", and marked Urgent citing '{matched_sev_words[0]}'"
        
    reason = f"Classified as {category} {reason_cat_part}{reason_sev_part}."
    
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
    Must handle missing data and not crash on bad rows.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Warning: skipped row due to error - {e}")
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
