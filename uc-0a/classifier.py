"""
UC-0A — Complaint Classifier
Built using AI based on RICE constraints in agents.md and skills from skills.md.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Map categories to specific keywords to accurately enforce classification boundaries
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlog", "inundated"],
    "Streetlight": ["streetlight", "street light", "lights out", "dark at night", "sparking"],
    "Waste": ["garbage", "waste", "trash", "dump", "dead animal", "rubbish"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["road surface", "broken", "crack"],
    "Heritage Damage": ["heritage damaged", "monument broken", "statue"],
    "Heat Hazard": ["heat", "sunstroke", "extreme temperature"],
    "Drain Blockage": ["drain", "manhole", "sewage", "clogged"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE rules in agents.md.
    """
    description = row.get("description", "").lower()
    
    # 1. Enforce Priority Output
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', description):
            priority = "Urgent"
            break
            
    # 2. Enforce Category Classification
    matched_cats = []
    reason_keywords = []
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in description:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                reason_keywords.append(kw)
                
    # 3. Handle Ambiguity & Constraints from agents.md
    if len(matched_cats) == 1:
        category = matched_cats[0]
        reason = f"Assigned to {category} because '{reason_keywords[0]}' was explicitly stated in description."
        flag = ""
    elif len(matched_cats) > 1:
        category = "Other"
        reason = f"Genuinely ambiguous: description contains indicators for multiple categories ({', '.join(matched_cats)})."
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        reason = "Genuinely ambiguous: could not map any specific keywords to a prescribed category based on description alone."
        flag = "NEEDS_REVIEW"
            
    out_row = dict(row)
    out_row["category"] = category
    out_row["priority"] = priority
    out_row["reason"] = reason
    out_row["flag"] = flag
    return out_row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results to output path safely.
    Follows error handling skill requirements defined in skills.md.
    """
    # First, read all rows to determine fieldnames
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        # Ensure we have the base headers plus the new classification headers expected
        fieldnames = reader.fieldnames
        if "category" not in fieldnames:
            fieldnames.extend(["category", "priority", "reason", "flag"])
        
    # Process and write output
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                # Flag nulls and malformed skips
                if not row or not any(row.values()):
                    continue
                if not row.get("description"):
                    # Missing critical info, apply fallback based on skills.md
                    error_row = dict(row)
                    error_row["category"] = "Other"
                    error_row["priority"] = "Low"
                    error_row["reason"] = "Input ambiguous or invalid: missing description."
                    error_row["flag"] = "NEEDS_REVIEW"
                    writer.writerow(error_row)
                    continue

                classified_row = classify_complaint(row)
                writer.writerow(classified_row)
                
            except Exception as e:
                # Continue gracefully on bad rows (as per skill error handling rule)
                error_row = dict(row)
                error_row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"System processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                # Add any missing keys to error_row that are in fieldnames
                for fn in fieldnames:
                    if fn not in error_row:
                        error_row[fn] = ""
                writer.writerow(error_row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Processed classifications. Results written to {args.output}")
