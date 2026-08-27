import argparse
import csv
import re

# Strict Taxonomy
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity Keywords
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Taxonomy Keyword Mapping (Robustness)
CATEGORY_MAP = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flooding", "floods", "waterlogging", "underpass flooded"],
    "Streetlight": ["streetlight", "lights out", "flickering", "dark at night"],
    "Waste": ["garbage", "trash", "waste", "dumped", "smell"],
    "Noise": ["noise", "music", "loud", "midnight"],
    "Road Damage": ["cracked", "sinking", "surface", "road damage"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sun", "shade"],
    "Drain Blockage": ["drain", "sewage", "blocked", "overflowing drain"],
}

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    
    # 1. Determine Category
    matched_category = "Other"
    found_keywords = []
    
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in description:
                matched_category = cat
                found_keywords.append(kw)
                break
        if matched_category != "Other":
            break
            
    # 2. Determine Priority
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            break
            
    # 3. Generate Reason
    if matched_category != "Other":
        reason = f"Classified as {matched_category} due to mentions of '{', '.join(found_keywords)}'."
    else:
        reason = "Classified as Other because no specific category keywords were found."
        
    # 4. Set Flag
    flag = ""
    # Flag if multiple categories matched or if "Other"
    matches = [cat for cat, kws in CATEGORY_MAP.items() if any(kw in description for kw in kws)]
    if len(matches) > 1 or matched_category == "Other":
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(classify_complaint(row))
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
