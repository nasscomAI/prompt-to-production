"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlog"],
    "Streetlight": ["streetlight", "light out", "lights out", "dark", "sparking"],
    "Waste": ["garbage", "waste", "dumped", "animal"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface", "manhole", "footpath", "broken", "cracked", "sinking", "tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain blocked", "drainage", "sewer", "drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    matched_categories = []
    for cat, keywords in CATEGORY_RULES.items():
        if any(kw in description for kw in keywords):
            matched_categories.append(cat)
            
    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Ambiguous multiple categories
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority & Reason
    priority = "Standard"
    reason_words = []
    
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            reason_words.append(keyword)
            
    if reason_words:
        reason = f"Severity keywords matched: {', '.join(reason_words)}."
    elif category != "Other" and flag != "NEEDS_REVIEW":
        matched_kw = []
        for kw in CATEGORY_RULES.get(category, []):
             if kw in description:
                 matched_kw.append(kw)
        reason = f"Category keyword matched: {', '.join(matched_kw)}."
    else:
        reason = "Could not definitively classify description without ambiguity."

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
    fieldnames = []
    rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames:
             fieldnames = list(reader.fieldnames)
        
        # Ensure our new fields are there
        for f in ["category", "priority", "reason", "flag"]:
            if f not in fieldnames:
                fieldnames.append(f)
                
        for row in reader:
            try:
                classification = classify_complaint(row)
                row["category"] = classification["category"]
                row["priority"] = classification["priority"]
                row["reason"] = classification["reason"]
                row["flag"] = classification["flag"]
            except Exception as e:
                row["category"] = "Other"
                row["priority"] = "Standard"
                row["reason"] = f"Processing error: {str(e)}"
                row["flag"] = "NEEDS_REVIEW"
                
            rows.append(row)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
