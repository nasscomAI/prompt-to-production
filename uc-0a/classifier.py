"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
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
    "Flooding": ["flood", "waterlogged", "waterlogging", "submerged"],
    "Streetlight": ["streetlight", "light", "dark", "lamp"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "animal"],
    "Noise": ["noise", "loud", "music"],
    "Road Damage": ["road", "cracked", "broken", "footpath", "tiles"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "sun", "hot"],
    "Drain Blockage": ["drain", "clogged", "sewage", "blockage", "manhole"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the rules defined in agents.md.
    Returns: dict with original data plus keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "No specific keywords found."
    flag = ""
    
    # Rule: Missing/Invalid description
    if not description:
        row.update({
            "category": "Other",
            "priority": "Low",
            "reason": "The description is empty or missing.",
            "flag": "ERROR"
        })
        return row

    # Rule: Determine Priority based on severity keywords
    urgent_words_found = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if urgent_words_found:
        priority = "Urgent"

    # Rule: Determine Category and catch ambiguous cases
    matched_categories = set()
    trigger_words = []
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in description:
                matched_categories.add(cat)
                trigger_words.append(kw)

    matched_categories = list(matched_categories)
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        if urgent_words_found:
            reason = f"Classified as {category} based on '{trigger_words[0]}', and set to Urgent because it mentions '{urgent_words_found[0]}'."
        else:
            reason = f"Classified as {category} because the description contains the word '{trigger_words[0]}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Description is ambiguous because it matches multiple categories: {', '.join(matched_categories)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not definitively determine a category from the description alone."

    row.update({
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    })
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.
    Must handle errors gracefully to ensure an output file is produced.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            
            # Ensure classification fields are included in output
            for field in ["category", "priority", "reason", "flag"]:
                if field not in fieldnames:
                    fieldnames.append(field)
                    
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    # Gracefully continue without crashing
                    row.update({
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "ERROR"
                    })
                    results.append(row)
                    
        # Write results
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Critical error during batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
