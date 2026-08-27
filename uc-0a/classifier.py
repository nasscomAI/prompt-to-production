"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Categories from agents.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "floods"],
    "Streetlight": ["streetlight", "light", "unlit", "dark"],
    "Waste": ["waste", "garbage", "bin", "animal", "dumped"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["crack", "sinking", "subsidence", "tiles broken", "paving"],
    "Heritage Damage": ["heritage", "ancient"],
    "Heat Hazard": ["heat", "temperature", "melting", "44°c", "45°c", "52°c", "sun", "burns", "heatwave"],
    "Drain Blockage": ["drain blocked", "drainage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md and skills.md.
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Priority
    priority = "Standard"
    matched_severity = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            matched_severity = kw
            break
            
    # 2. Determine Category
    matched_categories = []
    reason_keyword = ""
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    reason_keyword = kw
    
    # 3. Apply Enforcement Rules & Flagging
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason = f"The issue was classified as {category} because the description mentions '{reason_keyword}'."
    else:
        # Ambiguous (0 or multiple matches)
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The description does not clearly match a single category or is ambiguous."
        
    if priority == "Urgent":
        reason += f" It is marked Urgent due to the severity keyword '{matched_severity}'."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    fieldnames = reader.fieldnames
    if "category" not in fieldnames:
        fieldnames.extend(["category", "priority", "reason", "flag"])
        
    # Overwrite if exists
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                classification = classify_complaint(row)
                row.update(classification)
                writer.writerow(row)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                row["category"] = "Other"
                row["flag"] = "NEEDS_REVIEW"
                row["reason"] = f"Error processing: {str(e)}"
                writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
