"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # 1. Category logic (Taxonomy based on uc-0a/README.md)
    # Allowed: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
    category = "Other"
    
    # Keyword list per category
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "water", "inaccessible due to rain"],
        "Streetlight": ["streetlight", "lights out", "flickering", "dark at night", "lights out"],
        "Waste": ["garbage", "waste", "dead animal", "rubbish", "refuse", "dumped"],
        "Noise": ["noise", "music", "loud", "past midnight"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "shade"],
        "Drain Blockage": ["drain", "sewage", "blockage", "drainage"],
        "Road Damage": ["road surface", "cracked", "sinking", "paving", "broken footpath", "tiles broken"]
    }
    
    matched_cat_keywords = []
    for cat, keywords in cat_keywords.items():
        found = [kw for kw in keywords if kw in desc_lower]
        if found:
            category = cat
            matched_cat_keywords.extend(found)
            # Break on first match to avoid multiple categories, or prioritize
            break
    
    # 2. Priority logic (Severity keywords)
    # Keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    priority = "Standard"
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    found_urgent = [kw for kw in urgent_keywords if kw in desc_lower]
    if found_urgent:
        priority = "Urgent"
    # Note: Description says Urgent if severity keywords present. Otherwise Standard or Low.
    # Defaulting to Standard as per logic.
    
    # 3. Reason logic (One sentence, cite specific words)
    trigger_words = matched_cat_keywords + found_urgent
    if not trigger_words:
        reason = f"Classified because the description mentions no specific category keywords, but describes a general concern."
    else:
        # Sort and deduplicate for a cleaner reason
        unique_triggers = sorted(list(set(trigger_words)))
        reason = f"Classified as {category} with {priority} priority because the description mentions '{', '.join(unique_triggers)}'."

    # 4. Flag logic (NEEDS_REVIEW if ambiguous or Other)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id"),
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
        print(f"Error: Input file {input_path} does not exist.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
                
    if not results:
        print("No results to write.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
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
