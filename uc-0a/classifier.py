import argparse
import csv

CATEGORY_MAP = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlog", "submerge"],
    "Streetlight": ["streetlight", "light out", "lights out", "flicker", "dark"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dead animal"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["cracked", "sinking", "tiles broken", "broken road", "road surface", "manhole"],
    "Heritage Damage": ["heritage", "historic", "monument"],
    "Heat Hazard": ["heat", "temperature", "hot"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drain", "clogged", "sewer"],
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    
    # Priority
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            break
            
    # Category
    matched_categories = []
    matched_words = []
    
    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in description:
                if category not in matched_categories:
                    matched_categories.append(category)
                    matched_words.append(kw)
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason_word = matched_words[0]
        flag = ""
    else:
        # Ambiguous or no match
        category = matched_categories[0] if len(matched_categories) > 1 else "Other"
        reason_word = matched_words[0] if len(matched_words) > 0 else "unknown issue"
        flag = "NEEDS_REVIEW"
        
    reason = f"The description mentions '{reason_word}'."
    
    # Update row
    out_row = row.copy()
    out_row["category"] = category
    out_row["priority"] = priority
    out_row["reason"] = reason
    out_row["flag"] = flag
    
    return out_row

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        
        rows = list(reader)
        
    with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            classified_row = classify_complaint(row)
            writer.writerow(classified_row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
