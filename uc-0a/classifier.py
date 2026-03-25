"""
UC-0A — Complaint Classifier
Updated using RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os

# Priority keywords as defined in agents.md
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Category keyword mapping for the rule-based classifier
# Restricted to: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
CATEGORY_MAPPING = {
    "Pothole": ["pothole", "pit"],
    "Flooding": ["flood", "waterlogging", "inundation", "water log"],
    "Streetlight": ["streetlight", "street light", "lamp", "darkness", "light out"],
    "Waste": ["waste", "garbage", "trash", "dump", "litter", "animal"],
    "Noise": ["noise", "loud", "sound", "music"],
    "Road Damage": ["road damage", "crack", "pavement", "broken road", "footpath", "tile"],
    "Heritage Damage": ["heritage", "monument", "statue", "historical site"],
    "Heat Hazard": ["heat", "extreme temperature", "sunstroke"],
    "Drain Blockage": ["drain", "sewage", "clogged", "sewer", "blockage", "manhole"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, description, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # 1. Determine Category
    category = "Other"
    found_category = False
    matched_keyword = ""
    
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_category = True
                matched_keyword = kw
                break
        if found_category:
            break
            
    # 2. Determine Priority
    priority = "Standard"
    found_urgent_kw = []
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            found_urgent_kw.append(kw)
    
    # 3. Handle ambiguous cases (RICE Rule 4)
    flag = ""
    if category == "Other" or not description.strip():
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 4. Generate Reason (RICE Rule 3) -cite specific words
    if found_category and matched_keyword:
        reason = f"Category '{category}' assigned because the term '{matched_keyword}' was found in the input."
    elif flag == "NEEDS_REVIEW":
        reason = f"Category set to 'Other' as no specific category keywords were identified and the request might be ambiguous."
    else:
        reason = f"Classified as '{category}' using general descriptive context."

    if priority == "Urgent":
        reason += f" Priority elevated to Urgent due to keywords: {', '.join(found_urgent_kw)}."

    return {
        "complaint_id": complaint_id,
        "description": row.get("description", ""),
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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "Error"),
                        "description": row.get("description", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input CSV: {e}")
        return

    if results:
        fieldnames = results[0].keys()
        try:
            with open(output_path, mode='w', encoding='utf-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Failed to write output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
