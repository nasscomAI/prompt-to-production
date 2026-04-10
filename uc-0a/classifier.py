"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Enforcement Rule 2: Priority Keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_found = [word for word in urgent_keywords if re.search(r'\b' + re.escape(word) + r'\b', description)]
    
    priority = "Urgent" if urgent_found else "Standard"

    # Enforcement Rule 1: Category Mapping
    category_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogged", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "dump", "animal"],
        "Noise": ["noise", "music"],
        "Road Damage": ["road", "cracked", "broken", "sinking", "footpath", "tiles"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "sunburn"],
        "Drain Blockage": ["drain", "manhole", "sewage"]
    }

    matched_categories = set()
    found_keywords = []

    for cat, kws in category_map.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', description):
                matched_categories.add(cat)
                found_keywords.append(kw)

    # Enforcement Rule 4: Ambiguity Flag
    flag = ""
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
    elif len(matched_categories) > 1:
        # Handle certain mixed cases or genuinely ambiguous descriptions
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Enforcement Rule 3: Single sentence reason citing words
    cited_word = found_keywords[0] if found_keywords else "unspecified issue"
    reason_parts = []
    
    if flag == "NEEDS_REVIEW":
        reason = f"The description is flagged for review because it cites ambiguous or multiple issues like '{cited_word}'."
    else:
        if priority == "Urgent":
            reason = f"Categorized as {category} and marked Urgent because it mentions '{cited_word}' and severity keyword '{urgent_found[0]}'."
        else:
            reason = f"Categorized as {category} with Standard priority because the description mentions '{cited_word}'."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "date_raised": row.get("date_raised", ""),
        "city": row.get("city", ""),
        "ward": row.get("ward", ""),
        "location": row.get("location", ""),
        "description": row.get("description", ""),
        "reported_by": row.get("reported_by", ""),
        "days_open": row.get("days_open", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    fieldnames = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Skipping malformed row {row.get('complaint_id', 'UNKNOWN')}: {e}")
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Ensure our required output fields are present
    for field in ["category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)

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
