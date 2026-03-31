"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import traceback

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the RICE rules defined in agents.md.
    """
    description = row.get("description", "").lower()
    
    # Priority Enforcement
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in description]
    
    priority = "Standard"
    if found_urgent:
        priority = "Urgent"

    # Category Enforcement
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "water": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "dark": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road damage": "Road Damage",
        "crack": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
    }
    
    matched_categories = set()
    reason_words = []
    
    for kw, cat in category_map.items():
        if kw in description:
            matched_categories.add(cat)
            reason_words.append(kw)
            
    # Ambiguity logic
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No specific category keywords found in description."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Multiple categories matched ({', '.join(matched_categories)}) using words like '{reason_words[0]}' and '{reason_words[1]}'."
    else:
        category = list(matched_categories)[0]
        reason = f"The description mentions '{reason_words[0]}', mapping clearly to this category."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely process all rows even if some fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            # We want to output all original plus the new columns
            out_fields = fieldnames + ["category", "priority", "reason", "flag"]
            
            rows_to_write = []
            
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    # Merge classification results into the row
                    for k, v in classification.items():
                        if k != "complaint_id":
                            row[k] = v
                    rows_to_write.append(row)
                except Exception as e:
                    # Do not crash on bad rows
                    print(f"Failed to process row {row.get('complaint_id')}: {e}")
                    # Give it blank fallbacks
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = "Failed processing due to error."
                    row["flag"] = "NEEDS_REVIEW"
                    rows_to_write.append(row)
                    
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(rows_to_write)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
