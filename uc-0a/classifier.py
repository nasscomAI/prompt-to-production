"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on text matching.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    # Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "animal", "dump"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["crack", "road surface", "tiles broken", "manhole", "sinking"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain"]
    }

    matched_categories = []
    matched_word = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_word = kw

    # If exactly one category matched
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Ambiguous or none
        category = matched_categories[0] if matched_categories else "Other"
        flag = "NEEDS_REVIEW"
        matched_word = matched_word if matched_word else "no clear keywords"

    # 2. Determine Priority
    # Urgent if description contains one of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    priority = "Standard"
    urgent_word = None
    for ukw in urgent_keywords:
        if ukw in desc:
            priority = "Urgent"
            urgent_word = ukw
            break

    # 3. Reason
    if priority == "Urgent":
        reason = f"Flagged as {category} and Urgent due to keywords '{matched_word}' and '{urgent_word}'."
    else:
        reason = f"Classified as {category} based on the presence of '{matched_word}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in, \
             open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            
            reader = csv.DictReader(f_in)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    res = classify_complaint(row)
                    writer.writerow(res)
                except Exception as row_error:
                    print(f"Skipping malformed row {row.get('complaint_id', '?')}: {row_error}")
                    
    except Exception as e:
        print(f"Fatal error processing file {input_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
