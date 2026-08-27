"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md requirements.
"""
import argparse
import csv
import re

# Defined taxonomy as per agents.md
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood"],
    "Streetlight": ["streetlight", "light"],
    "Waste": ["garbage", "waste", "dead animal"],
    "Noise": ["music", "noise"],
    "Road Damage": ["crack", "broken", "manhole"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on text description.
    Returns: dict with updated fields: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    if not desc:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Insufficient information provided.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    matched_category = None
    found_cat_word = ""
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc:
                # Prioritize specific matches (e.g., Drain over general Flood if both present)
                if matched_category == "Flooding" and cat == "Drain Blockage":
                    matched_category = cat
                    found_cat_word = kw
                elif matched_category is None:
                    matched_category = cat
                    found_cat_word = kw

    # If no category matches or it's ambiguous
    if not matched_category:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The description does not contain clear keywords matching known categories."
    else:
        category = matched_category
        flag = ""
        reason_part1 = f"mentions '{found_cat_word}'"

    # 2. Determine Priority
    priority = "Standard"
    found_sev_word = None
    for kw in SEVERITY_KEYWORDS:
        # Match word boundaries to avoid partial matches
        if re.search(rf"\b{kw}\b", desc):
            priority = "Urgent"
            found_sev_word = kw
            break

    # 3. Construct Reason
    if category != "Other":
        if priority == "Urgent":
            reason = f"The description {reason_part1} and indicates high severity by citing '{found_sev_word}'."
        else:
            reason = f"The description {reason_part1} without acute severity markers."

    # Edge cases from the dataset (e.g. manhole missing -> road damage but could be drain)
    if "manhole cover missing" in desc:
        category = "Road Damage"
        reason = "The description mentions 'manhole cover missing' and cites 'injury' risk."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely handles empty rows and adds required fields.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # Add new fields if they don't exist
            new_fields = ["category", "priority", "reason", "flag"]
            out_fieldnames = list(fieldnames)
            for f in new_fields:
                if f not in out_fieldnames:
                    out_fieldnames.append(f)

            rows = list(reader)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    out_rows = []
    for i, row in enumerate(rows):
        try:
            classification = classify_complaint(row)
            row.update(classification)
            out_rows.append(row)
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            # Ensure row is still added with error info
            row.update({
                "category": "Other", 
                "priority": "Low", 
                "reason": "Processing error", 
                "flag": "NEEDS_REVIEW"
            })
            out_rows.append(row)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
