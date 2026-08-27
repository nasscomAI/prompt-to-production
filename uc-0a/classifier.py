"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get('description', '')).lower()
    complaint_id = row.get('complaint_id', '')

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Determine Category
    assigned_category = "Other"
    found_keywords = []
    
    if "pothole" in description:
        assigned_category = "Pothole"
        found_keywords.append("pothole")
    elif "flood" in description or "waterlogging" in description or "water" in description:
        assigned_category = "Flooding"
        found_keywords.append("flood/water")
    elif "light" in description:
        assigned_category = "Streetlight"
        found_keywords.append("light")
    elif "garbage" in description or "waste" in description or "trash" in description:
        assigned_category = "Waste"
        found_keywords.append("waste/garbage")
    elif "noise" in description or "loud" in description or "music" in description:
        assigned_category = "Noise"
        found_keywords.append("noise")
    elif "road" in description and "damage" in description:
        assigned_category = "Road Damage"
        found_keywords.append("road damage")
    elif "heritage" in description:
        assigned_category = "Heritage Damage"
        found_keywords.append("heritage")
    elif "heat" in description:
        assigned_category = "Heat Hazard"
        found_keywords.append("heat")
    elif "drain" in description or "block" in description:
        assigned_category = "Drain Blockage"
        found_keywords.append("drain/block")
    
    # Priority
    priority = "Standard"
    found_severity = []
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            found_severity.append(kw)
    
    # Reason
    if found_keywords or found_severity:
        words_cited = found_keywords + found_severity
        reason = f"Classified based on the presence of words: {', '.join(words_cited)}."
    else:
        reason = "Could not identify any specific target keywords in the description."

    # Flag
    flag = ""
    if assigned_category == "Other" or not description.strip():
        flag = "NEEDS_REVIEW"
        assigned_category = "Other"
        
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row:
                    results.append(classify_complaint(row))
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
