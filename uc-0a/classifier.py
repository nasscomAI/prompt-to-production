import argparse
import csv
import re

# RICE Enforcement Categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords for Priority enforcement
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Category keywords for simplistic ruling
CATEGORY_MAPPING = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "floods"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["waste", "dumped", "garbage", "trash", "smell"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["cracked", "sinking", "surface", "manhole"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain", "blocked"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    desc = row.get("description", "").lower()
    location = row.get("location", "").lower()
    combined_text = f"{desc} {location}"
    
    # 1. Determine Priority based on severity keywords (Enforcement rule 2)
    priority = "Standard"
    matched_severity = []
    for word in SEVERITY_KEYWORDS:
        if re.search(rf"\b{word}\b", combined_text):
            priority = "Urgent"
            matched_severity.append(word)
    if priority == "Standard" and "days_open" in row:
        try:
             if int(row["days_open"]) > 14:
                priority = "High"
             elif int(row["days_open"]) <= 3:
                priority = "Low"
        except ValueError:
             pass

    # 2. Determine Category based on keywords (Enforcement rule 1 & 4)
    matched_categories = set()
    category_reasons = {}
    
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if re.search(rf"\b{kw}\b", combined_text):
                matched_categories.add(cat)
                if cat not in category_reasons:
                    category_reasons[cat] = kw
    
    # Needs review logic (Enforcement rule 4)
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No clear category matched."
    elif len(matched_categories) > 1:
        # Resolve some overlap manually or flag it
        if "Waste" in matched_categories and "Drain Blockage" in matched_categories:
            category = "Drain Blockage"
            flag = ""
            reason = f"Keyword '{category_reasons['Drain Blockage']}' identified in text."
        elif "Road Damage" in matched_categories and "Pothole" in matched_categories:
            category = "Pothole"
            flag = ""
            reason = f"Keyword '{category_reasons['Pothole']}' identified in text."
        elif "Flooding" in matched_categories and "Drain Blockage" in matched_categories:
            category = "Flooding"
            flag = ""
            reason = f"Keyword '{category_reasons['Flooding']}' identified in text."
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            cats_str = ", ".join(matched_categories)
            reason = f"Ambiguous: matched multiple categories ({cats_str})."
    else:
        category = list(matched_categories)[0]
        flag = ""
        reason = f"Keyword '{category_reasons[category]}' identified in text."

    # Enforcement rule 3: Reason must cite specific words
    if matched_severity:
        sev_str = ", ".join(matched_severity)
        reason += f" Priority set to Urgent due to severity keywords: '{sev_str}'."
    
    # Construct complete reason
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row computationally, write results CSV.
    """
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = []
        if reader.fieldnames:
            for f in (reader.fieldnames or []):
                fieldnames.append(f)
        
    # Add new fieldnames
    new_fields = ["category", "priority", "reason", "flag"]
    for f in new_fields:
        if f not in fieldnames:
            fieldnames.append(f)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            try:
                classification = classify_complaint(row)
                row.update({
                    "category": classification.get("category", ""),
                    "priority": classification.get("priority", ""),
                    "reason": classification.get("reason", ""),
                    "flag": classification.get("flag", "")
                })
            except Exception as e:
                # Fallback on error
                row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error during processing: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
