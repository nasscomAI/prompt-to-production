import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

import re

CATEGORY_RULES = {
    "Pothole": [r"\bpotholes?\b"],
    "Flooding": [r"\bflood(ed|s|ing)?\b", r"\bwater\b"],
    "Streetlight": [r"\blights?\b", r"\bsparking\b", r"\bdark\b", r"\bstreetlights?\b"],
    "Waste": [r"\bgarbage\b", r"\bwaste\b", r"\banimals?\b", r"\btrash\b"],
    "Noise": [r"\bmusic\b", r"\bnoise\b", r"\bloud\b"],
    "Road Damage": [r"\bcrack(s|ed)?\b", r"\bsink(ing|s)?\b", r"\bbroken\b"],
    "Drain Blockage": [r"\bdrain(s|age)?\b", r"\bmanhole(s)?\b", r"\bblock(ed|age)?\b"],
    "Heritage Damage": [r"\bheritage\b"],
    "Heat Hazard": [r"\bheat\b", r"\bhot\b"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    
    # Handle null descriptions or complete ambiguity
    if not description.strip():
        row["category"] = "Other"
        row["priority"] = "Standard"
        row["reason"] = "No description provided."
        row["flag"] = "NEEDS_REVIEW"
        return row
        
    matched_categories = []
    matched_words = {}
    
    # 1. Determine category by evaluating ALL rules
    for cat, patterns in CATEGORY_RULES.items():
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_words[cat] = match.group(0)
    
    # Detect ambiguity (Failure Mode 5)
    if len(matched_categories) == 1:
        assigned_category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        # Multiple problems mentioned - flag for review
        assigned_category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine priority based on strict severity keywords with word boundaries
    priority = "Standard"
    matched_severity_word = None
    for keyword in SEVERITY_KEYWORDS:
        match = re.search(rf"\b{keyword}\b", description)
        if match:
            priority = "Urgent"
            matched_severity_word = match.group(0)
            break
            
    # 3. Justify with a strict one-sentence reason citing specific words (Failure Mode 3)
    if assigned_category != "Other":
        trigger_word = matched_words[assigned_category]
        if priority == "Urgent" and matched_severity_word:
            reason = f"Classified as {assigned_category} because it mentions '{trigger_word}', and marked Urgent due to the severity keyword '{matched_severity_word}'."
        else:
            reason = f"Classified as {assigned_category} because the description includes the word '{trigger_word}'."
    else:
        if priority == "Urgent" and matched_severity_word:
            reason = f"Classified as Other due to unrecognized issues, but marked Urgent because it contains the keyword '{matched_severity_word}'."
        else:
            reason = "Classified as Other because no known category keywords were clearly detected."
        
    row["category"] = assigned_category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)
        
        # Ensure our target columns exist in fieldnames
        for field in ["category", "priority", "reason", "flag"]:
            if field not in fieldnames:
                fieldnames.append(field)

        results = []
        for row in rows:
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Graceful degradation for bad rows
                row["category"] = "Other"
                row["priority"] = "Standard"
                row["reason"] = f"Error processing"
                row["flag"] = "NEEDS_REVIEW"
                results.append(row)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
