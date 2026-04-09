import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Keyword map for categories
    category_keywords = {
        "Pothole": ["pothole", "manhole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "animal", "dump"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["road surface", "crack", "sink", "tile", "footpath"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain"]
    }

    # Find matching keywords for priority
    matched_severity = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if matched_severity else "Standard"

    # Find matching categories
    matched_categories = []
    matched_words = []
    for cat, kws in category_keywords.items():
        cat_matches = [kw for kw in kws if kw in desc]
        if cat_matches:
            matched_categories.append(cat)
            matched_words.extend(cat_matches)
            
    # Ambiguity check and Category assignment
    if len(matched_categories) > 1:
        category = matched_categories[0] # Pick the first match
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Construct reason citing specific words
    reason_parts = []
    if matched_categories:
        reason_parts.append(f"Matched category '{category}' due to words: {', '.join(matched_words)}.")
    else:
        reason_parts.append("No specific category keywords found.")
        
    if matched_severity:
        reason_parts.append(f"Triggered 'Urgent' priority due to severity words: {', '.join(matched_severity)}.")
    else:
        reason_parts.append("No severity keywords found, defaulting to 'Standard'.")
        
    reason = " ".join(reason_parts)

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
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Don't crash on bad rows, just flag them
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed to process row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
Updated to trigger PR banner.
""")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
