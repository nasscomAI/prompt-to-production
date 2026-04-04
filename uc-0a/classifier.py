import argparse
import csv
import sys
import re

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description_lower = description.lower()
    
    # Priority classification based on explicit agents.md keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    found_urgent = [kw for kw in urgent_keywords if kw in description_lower]
    if found_urgent:
        priority = "Urgent"
        priority_reason = f"Contains severity keyword: '{found_urgent[0]}'."
    else:
        priority = "Standard"
        priority_reason = "No severity keywords found."

    # Category classification based on basic matching
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rain", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "dead animal", "smell", "dump"],
        "Noise": ["noise", "music", "loud"],
        "Drain Blockage": ["drain", "manhole"],
        "Road Damage": ["road surface", "footpath", "cracked", "road"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"]
    }

    matched_categories = []
    found_category_keyword = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            # simple regex to ensure word boundary
            if re.search(r'\b' + re.escape(kw) + r'\b', description_lower):
                matched_categories.append(cat)
                if not found_category_keyword:
                    found_category_keyword = kw
                break

    # If ambiguous (0 or >1 matches), set to Other and flag NEEDS_REVIEW
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reason = "Could not map to a standard category."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reason = f"Ambiguous description matches multiple categories: {', '.join(matched_categories)}."
    else:
        category = matched_categories[0]
        flag = ""
        cat_reason = f"Matches the keyword '{found_category_keyword}'."

    reason = f"{cat_reason} {priority_reason}"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            original_fieldnames = reader.fieldnames
            if not original_fieldnames:
                raise ValueError("Input CSV is empty or incorrectly formatted.")
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        sys.exit(1)

    output_rows = []
    
    for row in rows:
        description = row.get('description', '')
        
        # Skill: handle ambiguous or invalid inputs
        if not description or str(description).strip() == "":
            result = {
                "category": "Other",
                "priority": "Low",
                "reason": "Missing description input.",
                "flag": "NEEDS_REVIEW"
            }
        else:
            try:
                result = classify_complaint(description)
            except Exception as e:
                result = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {e}",
                    "flag": "NEEDS_REVIEW"
                }
        
        # Copy the original row precisely to preserve all unstripped columns
        output_row = row.copy()
        output_row["category"] = result["category"]
        output_row["priority"] = result["priority"]
        output_row["reason"] = result["reason"]
        output_row["flag"] = result["flag"]
        
        output_rows.append(output_row)

    # Write output to CSV safely
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            out_fieldnames = list(original_fieldnames) + ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as e:
        print(f"Error writing output CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
