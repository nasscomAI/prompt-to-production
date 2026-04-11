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
    Classifies a single complaint row using the municipal taxonomy and safety rules.
    """
    # Find description key dynamically
    desc_key = next((k for k in row.keys() if 'desc' in k.lower()), None)
    description = row.get(desc_key, "") if desc_key else ""
    desc_lower = description.lower()

    # 1. Determine Priority
    priority = "Standard"
    found_safety_words = [w for w in SAFETY_KEYWORDS if w in desc_lower]
    if found_safety_words:
        priority = "Urgent"
    elif "emergency" in desc_lower or "immediate" in desc_lower:
        priority = "Standard" # Defaulting if no safety words but urgent tone
    else:
        # Simple heuristic for 'Low'
        if any(w in desc_lower for w in ["eventually", "non-urgent", "suggestion"]):
            priority = "Low"

    # 2. Determine Category
    category = "Other"
    found_cat = None
    found_cat_words = []
    
    matches = []
    for cat, keywords in CATEGORY_MAPPING.items():
        match_words = [w for w in keywords if w in desc_lower]
        if match_words:
            matches.append((cat, match_words))

    flag = ""
    if len(matches) == 1:
        found_cat, found_cat_words = matches[0]
        category = found_cat
    elif len(matches) > 1:
        # Ambiguous if multiple matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        found_cat_words = [w for m in matches for w in m[1]]
    else:
        # No matches
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Generate Reason (Single sentence citing keywords)
    quoted_words = sorted(list(set(found_cat_words + found_safety_words)))
    if quoted_words:
        reason = f"Classified as {category} with {priority} priority due to the mention of '{', '.join(quoted_words)}' in the description."
    else:
        reason = f"Assigned to {category} as no specific municipal keywords were identified."
        if category == "Other":
            flag = "NEEDS_REVIEW"

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
