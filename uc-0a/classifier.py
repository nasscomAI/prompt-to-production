"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re
from typing import List, Dict

# Allowed categories and priorities
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# -------------------------------
# Skill: classify_complaint
# -------------------------------
def classify_complaint(complaint_text: str) -> Dict[str, str]:
    if not complaint_text or not complaint_text.strip():
        raise ValueError("Complaint description is missing or empty")

    complaint_lower = complaint_text.lower()
    # Simple keyword-based category assignment
    category = "Other"
    flag = ""

    category_keywords = {
        "Pothole": ["pothole", "hole in road"],
        "Flooding": ["flood", "waterlogging", "water log"],
        "Streetlight": ["streetlight", "lamp post", "light not working"],
        "Waste": ["garbage", "waste", "trash", "dumping"],
        "Noise": ["noise", "loud", "disturbance"],
        "Road Damage": ["road crack", "road damage", "uneven road"],
        "Heritage Damage": ["heritage", "monument", "historical damage"],
        "Heat Hazard": ["heat", "sun", "temperature"],
        "Drain Blockage": ["drain", "sewage", "blocked drain"]
    }

    matched_categories = []
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in complaint_lower:
                matched_categories.append(cat)
                break

    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Ambiguous category
        category = matched_categories[0]  # pick first
        flag = "NEEDS_REVIEW"

    # Enforce category allowed values
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority determination
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in complaint_lower:
            priority = "Urgent"
            break

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    # Reason: one sentence citing exact words
    # Take first sentence containing any category or severity keyword
    reason_sentences = re.split(r'(?<=[.!?])\s+', complaint_text.strip())
    reason = ""
    for sent in reason_sentences:
        for kw in SEVERITY_KEYWORDS + [cat.lower() for cat in ALLOWED_CATEGORIES]:
            if kw in sent.lower():
                reason = sent.strip()
                break
        if reason:
            break
    if not reason:
        reason = reason_sentences[0].strip()  # fallback to first sentence

    # Ensure reason is one sentence
    if len(re.findall(r'[.!?]', reason)) > 1:
        reason = reason.split('.')[0].strip() + '.'

    # Enforce flag is either NEEDS_REVIEW or blank
    if flag not in ["NEEDS_REVIEW", ""]:
        flag = ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

# -------------------------------
# Skill: batch_classify
# -------------------------------
def batch_classify(input_csv_path: str, output_csv_path: str):
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Input CSV file '{input_csv_path}' does not exist")

    rows_out = []

    with open(input_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'description' not in reader.fieldnames or 'complaint_id' not in reader.fieldnames:
            raise ValueError("Input CSV must contain 'description' and 'complaint_id' columns")

        for i, row in enumerate(reader, 1):
            description = row.get('description', '').strip()
            complaint_id = row.get('complaint_id', '').strip()
            if not description:
                raise ValueError(f"Row {i} missing complaint description")
            classified = classify_complaint(description)
            classified['complaint_id'] = complaint_id  # Add complaint_id to the output
            rows_out.append(classified)

    # Ensure row count consistency
    if len(rows_out) != sum(1 for _ in open(input_csv_path, 'r', encoding='utf-8')) - 1:
        raise ValueError("Row count mismatch between input and output")

    # Write output CSV
    # Ensure the directory for the output file exists, if specified
    output_dir = os.path.dirname(output_csv_path)
    if output_dir:  # Only create directories if a directory is specified
        os.makedirs(output_dir, exist_ok=True)

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as out_csv:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows_out:
            writer.writerow(row)

# -------------------------------
# Main CLI
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"Classification completed. Output written to {args.output}")
    except Exception as e:
        print(f"Error during classification: {e}")
        exit(1)

if __name__ == "__main__":
    main()