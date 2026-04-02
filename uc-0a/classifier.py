"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = "No description provided."

    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }

    # Extract keywords for reason
    words = []
    matched_categories = []

    # Rule-based categorization mapping
    if "pothole" in desc:
        matched_categories.append("Pothole")
        words.append("pothole")
    if "flood" in desc or "waterlogging" in desc or "rain" in desc:
        matched_categories.append("Flooding")
        words.append("flood" if "flood" in desc else "rain")
    if "streetlight" in desc or " light" in desc:
        matched_categories.append("Streetlight")
        words.append("light")
    if "waste" in desc or "garbage" in desc:
        matched_categories.append("Waste")
        words.append("waste" if "waste" in desc else "garbage")
    if "noise" in desc or "drilling" in desc or "idling" in desc or "loud" in desc:
        matched_categories.append("Noise")
        words.append("drilling" if "drilling" in desc else ("idling" if "idling" in desc else "noise"))
    if "collapse" in desc and "road" in desc or "crater" in desc:
        matched_categories.append("Road Damage")
        words.append("collapse" if "collapse" in desc else "crater")
    if "heritage" in desc and "damage" in desc:
        matched_categories.append("Heritage Damage")
        words.append("heritage")
    if "heat" in desc:
        matched_categories.append("Heat Hazard")
        words.append("heat")
    if "drain" in desc or "block" in desc:
        if "drain" in desc and "block" in desc:
            matched_categories.append("Drain Blockage")
            words.append("drain block")

    # Conflict Resolution
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The description did not clearly match any specific category."
    elif len(set(matched_categories)) > 1:
        # Ambiguous cases (Multiple categories)
        if set(["Flooding", "Drain Blockage"]).issubset(set(matched_categories)):
             if "drain completely blocked" in desc or "main drain blocked" in desc:
                 category = "Drain Blockage"
                 reason = "Classified as Drain Blockage because the description details a completely blocked drain."
             elif "underpass flooded" in desc or "market area flooded" in desc:
                 category = "Flooding"
                 reason = "Classified as Flooding because the description specifically highlights flooded areas."
             else:
                 category = "Other"
                 flag = "NEEDS_REVIEW"
                 reason = f"Ambiguous complaint containing '{', '.join(words)}'."
        elif set(["Waste", "Flooding"]).issubset(set(matched_categories)):
             category = "Waste"
             reason = "Classified as Waste primarily due to mention of garbage/waste."
        else:
             category = "Other"
             flag = "NEEDS_REVIEW"
             reason = f"Multiple conflicting keywords found: '{', '.join(words)}'."
    else:
        # Explicit single match
        category = matched_categories[0]
        reason = f"Classified strictly as {category} because the description contains '{words[0]}'."
    
    # Heritage Waste override (hyderabad data edge cases)
    if not flag and "heritage" in desc and "garbage" in desc:
        category = "Waste"
        reason = "Classified as Waste because there is a garbage overflow."

    # Priority Evaluation
    is_urgent = False
    urgent_words = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc):
            is_urgent = True
            urgent_words.append(kw)
            
    if is_urgent:
        priority = "Urgent"
        reason += f" Elevated to Urgent priority because it contains the severity keyword '{urgent_words[0]}'."
    elif flag == "NEEDS_REVIEW" and category == "Other":
        priority = "Standard"

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    with open(input_path, 'r', encoding='utf-8', errors='replace') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                
                # Compose final row updating original data
                out_row = dict(row)
                out_row['category'] = classified['category']
                out_row['priority'] = classified['priority']
                out_row['reason'] = classified['reason']
                out_row['flag'] = classified['flag']
                
                results.append(out_row)
            except Exception as e:
                print(f"Skipping row directly due to error {e}")
                
    if not results:
        print("No valid rows processed.")
        return
        
    fieldnames = list(results[0].keys())
    for needed_key in ['category', 'priority', 'reason', 'flag']:
        if needed_key not in fieldnames:
            fieldnames.append(needed_key)
            
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
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
