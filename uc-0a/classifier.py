"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogging", "inundated"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dead animal", "smell", "dumped"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["road damage", "crack", "sinking", "surface", "broken", "upturned"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "temperature"],
    "Drain Blockage": ["drain", "blockage", "clogged", "sewer", "manhole"]
}

VALID_CATEGORIES = list(CATEGORY_KEYWORDS.keys()) + ["Other"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine priority
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    priority = "Urgent" if found_severity else "Standard"
    
    # 2. Determine category
    matched_cats = []
    found_cat_words = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                found_cat_words.append(kw)
    
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
    else:
        # Ambiguous (0 or >1 matches)
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Special handling based on explicit dataset hints (e.g. 'heritage street, lights out' -> multiple matches)
    if "heritage" in desc and "light" in desc:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    # 3. Create reason citing exact words
    all_found_words = set(found_severity + found_cat_words)
    if all_found_words:
        words_str = ", ".join(f"'{w}'" for w in sorted(all_found_words))
        reason = f"Classified based on explicit keywords: {words_str} found in the description."
    else:
        reason = "No known category or severity keywords found in the description."
        category = "Other"
        flag = "NEEDS_REVIEW"
        
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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        results = []
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                # Fallback for bad rows
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error classifying row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
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
