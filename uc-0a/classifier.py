"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E enforcement rules.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Enforce Priority (Urgent if severity keywords present)
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    matched_severity = []
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            matched_severity.append(kw)
            
    # 2. Enforce Category (Exact strings only)
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flooded", "floods", "flood"],
        "Streetlight": ["streetlight", "lights out", "light out"],
        "Waste": ["waste", "garbage", "trash"],
        "Noise": ["noise", "music", "loud"],
        "Drain Blockage": ["drain blocked", "drain"],
        "Road Damage": ["crack", "sinking", "broken", "manhole"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"]
    }
    
    category = "Other"
    matched_cat = []
    flag = ""
    
    for cat, kws in categories.items():
        for kw in kws:
            if kw in desc:
                category = cat
                matched_cat.append(kw)
                break
        if category != "Other":
            break
            
    # 3. Enforce Refusal Condition (ambiguity, incomprehensible, or unrelated logging)
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Refused classification because the description is ambiguous, completely incomprehensible, or unrelated to city municipal services."
    else:
        cited_words = matched_cat + matched_severity
        reason = f"Classified as {category} with {priority} priority because the description mentions '{', '.join(cited_words)}'."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Skips crashes on bad rows and flags nulls.
    """
    results = []
    fieldnames = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        for row in reader:
            try:
                classification = classify_complaint(row)
                row['category'] = classification['category']
                row['priority'] = classification['priority']
                row['reason'] = classification['reason']
                row['flag'] = classification['flag']
                results.append(row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                row['category'] = "Other"
                row['priority'] = "Low"
                row['reason'] = f"Error during parsing: {str(e)}"
                row['flag'] = "NEEDS_REVIEW"
                results.append(row)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
