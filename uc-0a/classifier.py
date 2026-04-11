import argparse
import csv
import re
from typing import Dict

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row based on rules defined in agents.md and skills.md.
    Returns: A dictionary with the original data plus category, priority, reason, and flag columns.
    """
    description = row.get("description", "").lower()
    
    # Needs to determine: category, priority, reason, flag
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    matched_word = ""

    # Category Mapping
    category_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "submerged"],
        "Streetlight": ["streetlight", "light", "dark", "bulb"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "animal"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["crack", "surface", "broken", "manhole"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "sun", "temperature"],
        "Drain Blockage": ["drain", "clog", "blockage", "sewer"]
    }

    # 1. Determine Category
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_word = kw
                break
        if category != "Other":
            break

    # Flag for ambiguity
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason_sentence = "The issue cannot be clearly determined from the description alone."
    else:
        reason_sentence = f"The description contains '{matched_word}' justifying the {category} category."

    # 2. Determine Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    urgent_word = ""
    for word in severity_keywords:
        if re.search(r'\b' + re.escape(word) + r'\b', description):
            priority = "Urgent"
            urgent_word = word
            break

    if priority == "Urgent":
        reason_sentence += f" Priority elevated to Urgent due to keyword '{urgent_word}'."

    # Copy row and append metadata
    out_row = dict(row)
    out_row["category"] = category
    out_row["priority"] = priority
    out_row["reason"] = reason_sentence.strip()
    out_row["flag"] = flag
    
    return out_row


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, applies classify_complaint iteratively, and writes an output CSV.
    Safely bypasses null/malformed rows without crashing.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print("Error: Input file appears empty or lacks headers.")
                return

            original_rows = list(reader)
            # Append new columns for the results
            fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return

    classified_rows = []
    for num, row in enumerate(original_rows, start=1):
        try:
            processed = classify_complaint(row)
            classified_rows.append(processed)
        except Exception as e:
            print(f"Row {num} skipped due to error: {e}")
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified records mapped and written to {args.output}")
