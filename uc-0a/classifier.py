"""
UC-0A — Complaint Classifier
Implemented using RICE workflow: agents.md -> skills.md -> CRAFT.
"""
import argparse
import csv
import os

# Categories based on agents.md taxonomy
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords for priority: Urgent
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Keywords for categorization
CATEGORY_MAP = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water logged", "inundation"],
    "Streetlight": ["streetlight", "light out", "lights out", "dark at night", "flickering"],
    "Waste": ["waste", "garbage", "trash", "debris", "dead animal", "dumped"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road surface", "cracked", "sinking", "pavement"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sunstroke", "dehydration"],
    "Drain Blockage": ["drain blocked", "drainage", "sewage", "overflowing drain"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys matching original CSV + category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Identify Priority
    priority = "Standard"
    found_priority_keywords = [kw for kw in URGENT_KEYWORDS if kw in desc]
    if found_priority_keywords:
        priority = "Urgent"
    
    # Identify Category
    category = "Other"
    found_categories = []
    
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in desc for kw in keywords):
            found_categories.append(cat)
            
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        category = found_categories[0] # Pick first, but flag
    
    # Identify Reason (Drafting a one-sentence reason using words from description)
    # Simple reason generator: cite the keywords found
    keywords_to_cite = found_priority_keywords + [kw for kw in CATEGORY_MAP.get(category, []) if kw in desc]
    if not keywords_to_cite:
        # Fallback if no keywords found in the chosen category
        words = row.get("description", "").split()
        if len(words) > 5:
            cite_snippet = " ".join(words[:5])
        else:
            cite_snippet = row.get("description", "")
        reason = f"Classified based on report snippet: '{cite_snippet}'."
    else:
        reason = f"Classified as {category} due to mentions of '{', '.join(keywords_to_cite)}' in description."

    # Identify Flag
    flag = ""
    if category == "Other" or len(found_categories) > 1 or not found_categories:
        flag = "NEEDS_REVIEW"

    # Merge with original row data
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            for row in reader:
                classified_row = classify_complaint(row)
                results.append(classified_row)
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
