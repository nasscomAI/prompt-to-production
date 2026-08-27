"""
UC-0A — Complaint Classifier
Implementation based on the RICE framework from agents.md and skills.md.
Execution: Deterministic / Regex / Rule-Based (No External AI Tools).
"""
import argparse
import csv
import re
import os

# Taxonomy mapping isolated from agents.md context logic
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole in road"],
    "Flooding": ["flood", "waterlogging", "water logged", "overflow", "submerged"],
    "Streetlight": ["streetlight", "street light", "darkness", "lamp", "no light", "bulb"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "smell", "bin"],
    "Noise": ["noise", "loud", "music", "construction sound", "decibel", "speaker"],
    "Road Damage": ["crack", "road damage", "broken asphalt", "broken road"],
    "Heritage Damage": ["heritage", "monument", "statue damage", "historical"],
    "Heat Hazard": ["heatwave", "extreme heat", "sunstroke", "heat hazard"],
    "Drain Blockage": ["drain", "clogged", "sewer", "blockage", "gutter", "choked"]
}

# Strict urgent enforcements isolated from agents.md enforcement triggers
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row utilizing explicit pattern matchings.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    description_lower = description.lower()
    
    category = "Other"
    priority = "Standard"  # Lower default mapped conditionally 
    reason = ""
    flag = ""
    
    # 1. Enforcement Check 2: Severity Scanning
    matched_severity = []
    for sev in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(sev) + r'\b', description_lower):
            matched_severity.append(sev)
    
    if matched_severity:
        priority = "Urgent"
    elif "low" in description_lower and priority != "Urgent":
        # Additional safe mapping if not urgent
        priority = "Low"
    
    # 2. Enforcement Check 1: Categorical Scanning
    matched_categories = []
    for cat, kw_list in CATEGORY_KEYWORDS.items():
        for kw in kw_list:
            if re.search(r'\b' + re.escape(kw) + r'\b', description_lower):
                matched_categories.append((cat, kw))
                break # Extract only the first match internally per category
                
    # 3. Validation Logic and Output structuring
    if len(matched_categories) == 1: # Explicit mapping
        category = matched_categories[0][0]
        primary_kw = matched_categories[0][1]
        sev_text = f" and triggered severity keyword '{matched_severity[0]}'" if matched_severity else ""
        reason = f"Contains '{primary_kw}'{sev_text}."
    elif len(matched_categories) > 1: # Ambiguity resolution triggers NEEDS_REVIEW
        category = "Other"
        flag = "NEEDS_REVIEW"
        ambiguous_types = ', '.join([c[0] for c in matched_categories])
        reason = f"Ambiguous categories matched: {ambiguous_types}."
    elif not description.strip():  # Complete failure
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Empty description."
    else: # Total miss
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently determine category from description."

    return {
        "complaint_id": row.get("complaint_id", "unknown"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row deterministically, write results CSV.
    Must: flag nulls, not crash on bad rows.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    fieldnames = ["complaint_id", "description", "category", "priority", "reason", "flag"]

    print(f"Reading batch data from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classification = classify_complaint(row)
            
            output_row = {
                "complaint_id": classification["complaint_id"],
                "description": row.get("description", ""),
                "category": classification["category"],
                "priority": classification["priority"],
                "reason": classification["reason"],
                "flag": classification["flag"]
            }
            results.append(output_row)

    print(f"Processed {len(results)} rows. Saving aggregations...")
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
