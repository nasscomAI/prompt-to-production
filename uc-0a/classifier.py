"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re
import os

# Classification Schema Constants
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "hole"],
    "Flooding": ["flood", "waterlogging", "inundation", "water log"],
    "Streetlight": ["streetlight", "lamp", "light out", "dark street"],
    "Waste": ["garbage", "trash", "waste", "dumping", "refuse"],
    "Noise": ["noise", "loud", "sound", "music", "disturbance"],
    "Road Damage": ["crack", "pavement", "broken road", "asphalt"],
    "Heritage Damage": ["heritage", "monument", "statue", "ancient", "historical"],
    "Heat Hazard": ["heat", "sun", "shade", "dehydration", "extreme temp"],
    "Drain Blockage": ["drain", "gutter", "sewer", "blocked", "overflowing"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Enforces rules from agents.md:
    1. Exact category strings.
    2. Priority 'Urgent' if keywords present.
    3. One-sentence reason citing description.
    4. 'NEEDS_REVIEW' flag for ambiguity.
    """
    description = str(row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category
    matched_categories = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in description for kw in keywords):
            matched_categories.append(cat)
    
    category = "Other"
    flag = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = matched_categories[0] # Pick first match
        flag = "NEEDS_REVIEW" # Multiple matches indicate ambiguity
    else:
        category = "Other"
        if description.strip() == "":
            flag = "NEEDS_REVIEW"
            
    # 2. Determine Priority
    found_urgent_words = [word for word in URGENT_KEYWORDS if word in description]
    priority = "Urgent" if found_urgent_words else "Standard"
    
    # 3. Generate Reason
    if description.strip():
        if found_urgent_words:
            reason = f"Classified as {category} with {priority} priority because the description mentions '{found_urgent_words[0]}'."
        elif category != "Other":
            # Find the keyword that triggered the category
            trigger_word = next((kw for kw in CATEGORY_KEYWORDS[category] if kw in description), "keyword")
            reason = f"The mention of '{trigger_word}' indicates this belongs to the {category} category."
        else:
            reason = "Category set to Other as no specific keywords were identified."
    else:
        reason = "Empty description; defaulting to Other/Standard."
        flag = "NEEDS_REVIEW"

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
    Handles nulls and continues processing on errors.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping row due to error: {e}")
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if not results:
        print("No results to write.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
