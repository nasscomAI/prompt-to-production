import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogging", "submerged"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["waste", "garbage", "trash", "rubbish"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["road damage", "broken road", "cracked"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "wave"],
    "Drain Blockage": ["drain", "blocked", "sewer", "sewage"],
}

def classify_complaint(row: dict) -> dict:
    description = row.get("complaint", row.get("description", ""))
    description_lower = description.lower()
    
    # Determine Category
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in description_lower for keyword in keywords):
            matched_categories.append(category)
            
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = ""
        
    # Determine Priority
    urgent_keywords_found = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
    if urgent_keywords_found:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Reason
    if urgent_keywords_found:
        reason = f"The description mentions the severity keyword '{urgent_keywords_found[0]}'."
    elif matched_categories and category != "Other":
        matched_kw = [kw for kw in CATEGORY_KEYWORDS[category] if kw in description_lower][0]
        reason = f"The description mentions the keyword '{matched_kw}'."
    else:
        first_word = description.split()[0] if description.split() else "unclear"
        reason = f"The description starts with '{first_word}'."
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            
            output_fieldnames = fieldnames.copy()
            for col in ["category", "priority", "reason", "flag"]:
                if col not in output_fieldnames:
                    output_fieldnames.append(col)
            
            results = []
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                    results.append(row)
                except Exception:
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = "Error processing row."
                    row["flag"] = "NEEDS_REVIEW"
                    results.append(row)
                    
        with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to process dataset: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
