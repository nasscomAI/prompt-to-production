"""
UC-0A — Complaint Classifier
Implementation based on RICE (agents.md) and skills.md.
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flooded", "flooding", "water", "stranded"],
    "Streetlight": [" streetlight", " light", "dark"],
    "Waste": ["garbage", " bin", "waste", "dumped", "animal", "smell"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "manhole", "footpath", "tiles", "broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "temperature", "sun"],
    "Drain Blockage": ["drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    best_match_count = 0
    flag = ""
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in description]
        if len(matches) > best_match_count:
            category = cat
            best_match_count = len(matches)
    
    if best_match_count == 0:
        flag = "NEEDS_REVIEW"
    
    # 2. Determine Priority
    priority = "Standard"
    found_severity_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if found_severity_keywords:
        priority = "Urgent"
    
    # 3. Create Reason
    if category != "Other":
        reason_evidence = f"Mentions {category.lower()} related issues like '{next(iter([kw for kw in CATEGORY_KEYWORDS[category] if kw in description]), '')}'."
    else:
        reason_evidence = "Category could not be definitively determined from the text."
    
    if priority == "Urgent":
        reason_evidence += f" Flagged as Urgent due to keywords like '{found_severity_keywords[0]}'."
    
    reason = f"Classified as {category} with {priority} priority. {reason_evidence}"
    
    # 4. Final outcome
    return {
        "complaint_id": row.get("complaint_id", "Unknown"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    headers = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = [h for h in (reader.fieldnames or [])]
            headers.extend(["category", "priority", "reason", "flag"])
            for row in reader:
                if not row.get("description"):
                    print(f"Warning: Skipping row {row.get('complaint_id')} due to missing description.")
                    continue
                
                classification = classify_complaint(row)
                row.update(classification)
                results.append(row)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
