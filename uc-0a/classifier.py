"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # Check for missing description
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = str(description).lower()
    
    # Enforcement Rule: Priority MUST BE 'Urgent' IF severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    reason_priority = ""
    for word in severity_keywords:
        if re.search(rf'\b{word}\b', desc_lower):
            priority = "Urgent"
            reason_priority = f"Description contains severity keyword '{word}'."
            break
            
    # Enforcement Rule: Category must be exactly one of the allowed categories
    categories = {
        "Pothole": ["pothole", "crater", "hole"],
        "Flooding": ["flood", "waterlogging", "waterlog", "submerge", "water logging"],
        "Streetlight": ["streetlight", "light", "lamp", "dark"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "smell"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["road damage", "crack", "broken road", "uneven"],
        "Heritage Damage": ["heritage", "monument", "statue", "historical"],
        "Heat Hazard": ["heat", "sun", "hot"],
        "Drain Blockage": ["drain", "block", "clog", "sewage", "gutter"]
    }
    
    found_categories = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if re.search(rf'\b{kw}\b', desc_lower) or kw in desc_lower:
                found_categories.append((cat, kw))
                
    assigned_category = "Other"
    reason_category = ""
    flag = ""
    
    if not found_categories:
        assigned_category = "Other"
        reason_category = "Could not determine category from description."
        flag = "NEEDS_REVIEW"
    else:
        unique_cats = list(set([c for c, k in found_categories]))
        if len(unique_cats) > 1:
            assigned_category = "Other"
            reason_category = f"Ambiguous description matching multiple categories: {', '.join(unique_cats)}."
            flag = "NEEDS_REVIEW"
        else:
            assigned_category = unique_cats[0]
            matched_kw = [k for c, k in found_categories if c == assigned_category][0]
            reason_category = f"Description mentions '{matched_kw}'."

    reason = ""
    if reason_category and reason_priority:
        reason = f"{reason_category} {reason_priority}"
    elif reason_category:
        reason = reason_category
    else:
        reason = reason_priority

    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
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
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    # Error handling: Skips invalid rows, logs errors, ensures output file is written
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
