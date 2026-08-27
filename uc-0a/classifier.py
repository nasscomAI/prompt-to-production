"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

# Constants from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SAFETY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPING = {
    "Pothole": ["pothole", "hole", "crater", "sinkhole"],
    "Flooding": ["flood", "water", "overflow", "rain", "submerged"],
    "Streetlight": ["light", "lamp", "dark", "street light", "bulb"],
    "Waste": ["trash", "garbage", "waste", "rubbish", "dump", "litter"],
    "Noise": ["noise", "loud", "sound", "party", "barking", "music"],
    "Road Damage": ["road", "pavement", "asphalt", "crack", "surface"],
    "Heritage Damage": ["heritage", "statue", "monument", "historic", "museum"],
    "Heat Hazard": ["heat", "hot", "sun", "temperature", "overheating"],
    "Drain Blockage": ["drain", "sewage", "clog", "blockage", "gutter"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row using the municipal taxonomy and safety rules defined in agents.md.
    """
    # Find description key dynamically (handle case sensitivity and common variations)
    desc_key = next((k for k in row.keys() if 'desc' in k.lower()), None)
    description = row.get(desc_key, "") if desc_key else ""
    desc_lower = description.lower()

    # 1. Determine Priority
    found_safety_words = [w for w in SAFETY_KEYWORDS if w in desc_lower]
    if found_safety_words:
        priority = "Urgent"
    else:
        # If no safety words, default to Standard, or Low if specific keywords found
        low_priority_keywords = ["eventually", "non-urgent", "suggestion", "low priority", "not urgent"]
        if any(w in desc_lower for w in low_priority_keywords):
            priority = "Low"
        else:
            priority = "Standard"

    # 2. Determine Category
    matches = []
    for cat, keywords in CATEGORY_MAPPING.items():
        match_words = [w for w in keywords if w in desc_lower]
        if match_words:
            matches.append((cat, match_words))

    category = "Other"
    flag = ""
    found_cat_words = []

    if len(matches) == 1:
        category, found_cat_words = matches[0]
    elif len(matches) > 1:
        # Genuinely ambiguous if multiple domains match
        category = "Other"
        flag = "NEEDS_REVIEW"
        # Collect all triggering words for the reason
        for _, words in matches:
            found_cat_words.extend(words)
    else:
        # No matches found in taxonomy
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Generate Reason (Exactly one sentence citing specific words)
    triggering_words = sorted(list(set(found_cat_words + found_safety_words)))
    if triggering_words:
        reason = f"This complaint is classified as {category} with {priority} priority because it mentions safety or municipal keywords such as '{', '.join(triggering_words)}'."
    else:
        reason = f"This complaint is assigned to {category} with {priority} priority as no specific municipal or safety keywords were identified in the description."

    return {
        "complaint_id": row.get("complaint_id", "N/A"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Process input CSV and write classification results to output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            input_fields = reader.fieldnames
            
            for row in reader:
                # Basic validation: flag nulls or empty descriptions
                desc_key = next((k for k in row.keys() if 'desc' in k.lower()), None)
                if not row.get(desc_key):
                    classification = {
                        "complaint_id": row.get("complaint_id", "MISSED"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing or empty description detected during triage.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    try:
                        classification = classify_complaint(row)
                    except Exception as e:
                        classification = {
                            "complaint_id": row.get("complaint_id", "ERROR"),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"System error during classification: {str(e)}",
                            "flag": "NEEDS_REVIEW"
                        }
                
                # Merge input row with classification results
                # Filtering out stripped columns if they exist
                clean_row = {k: v for k, v in row.items() if k not in ["category", "priority_flag"]}
                clean_row.update(classification)
                results.append(clean_row)

        if not results:
            print("Warning: No results generated. Check if the input file is empty.")
            return

        # Prepare output fieldnames
        # We want to keep the original ID if it was there, and add our results
        fieldnames = list(results[0].keys())

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Critical error during batch processing: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
