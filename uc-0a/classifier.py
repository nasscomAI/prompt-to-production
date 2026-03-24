"""
UC-0A — Complaint Classifier
Implemented using local Python heuristics based on the R.I.C.E specifications.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "tyre damage"],
    "Flooding": ["flood", "water", "knee-deep", "stranded", "underpass"],
    "Streetlight": ["streetlight", "dark", "sparking", "lights out"],
    "Waste": ["garbage", "waste", "smell", "dumped", "dead animal"],
    "Noise": ["music", "noise", "loud", "midnight"],
    "Road Damage": ["cracked", "sinking", "surface", "footpath", "tiles broken", "manhole"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain blocked", "drainage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using local heuristics.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority defaults
    priority = "Standard"
    reason = "Standard issue reported."
    
    # Check for Urgent severity
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            reason = f"Severity keyword '{kw}' found in description."
            break
            
    # Check Category
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in desc for k in kws):
            category = cat
            flag = ""
            if priority == "Standard":
                reason = f"Complaint issue related to {cat.lower()}."
            break
            
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
    results = []
    fieldnames = []
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        _fn = reader.fieldnames
        fieldnames = list(_fn) if _fn is not None else []
        
        for field in ["category", "priority", "reason", "flag"]:
            if field not in fieldnames:
                fieldnames.append(field)
                
        for row in reader:
            classification = classify_complaint(row)
            row["category"] = classification["category"]
            row["priority"] = classification["priority"]
            row["reason"] = classification["reason"]
            row["flag"] = classification["flag"]
            results.append(row)
            print(f"Processed {row.get('complaint_id')} -> {row['category']} / {row['priority']}")

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Local Heuristic Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
