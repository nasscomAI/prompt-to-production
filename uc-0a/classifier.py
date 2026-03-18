"""
UC-0A — Complaint Classifier
Rule-based heuristic implementation based strictly on agents.md enforcement rules.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "water"],
    "Streetlight": ["streetlight", "light", "dark", "sparking"],
    "Waste": ["garbage", "waste", "bin", "animal", "smell"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road", "crack", "surface", "tile", "footpath", "manhole"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with updated keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Priority
    found_severity = [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + kw + r'(s)?\b', desc)]
    priority = "Urgent" if found_severity else "Standard"
    
    # 2. Determine Category
    matched_categories = []
    matched_words = []
    
    for cat, kws in CATEGORY_RULES.items():
        for kw in kws:
            if re.search(r'\b' + kw + r'(s)?\b', desc) or kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_words.append(kw)
                
    category = ""
    flag = ""
    reason = ""
    
    if len(matched_categories) >= 1:
        # If multiple categories matched, we just pick the first one and flag if it's genuinely ambiguous
        # For this test, we could just pick the first match to keep it simple, unless it's truly competing.
        # Let's adjust rule 4: if multiple categories matched but one clearly dominates, or just flag it.
        # Actually, let's just flag if > 1 category matches.
        if len(matched_categories) == 1:
            category = matched_categories[0]
            reason = f"The complaint explicitly mentions '{matched_words[0]}'."
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = f"Genuinely ambiguous as it matches multiple categories: {', '.join(matched_categories)}."
    else:
        # Ambiguous or no match
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently classify based on the description alone."
            
    # Include priority reasoning if Urgent
    if priority == "Urgent":
        reason += f" Priority is Urgent due to severity keyword '{found_severity[0]}'."
        
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Failed to read {input_path}: {e}")
        return

    if not fieldnames:
        fieldnames = []
        
    for field in ["category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)

    out_rows = []
    for row in rows:
        try:
            classified_row = classify_complaint(row)
            out_rows.append(classified_row)
        except Exception as e:
            print(f"Failed classifying row {row.get('complaint_id', 'unknown')}: {e}")
            row["category"] = "Other"
            row["priority"] = "Standard"
            row["reason"] = "Processing failed."
            row["flag"] = "NEEDS_REVIEW"
            out_rows.append(row)

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)
    except Exception as e:
        print(f"Failed to write to {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
