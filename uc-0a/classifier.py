"""
UC-0A — Complaint Classifier
"""

import csv
import argparse

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(text):
    text_lower = text.lower()

    # Category detection
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "waterlogging" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower:
        category = "Noise"
    elif "road" in text_lower:
        category = "Road Damage"
    elif "drain" in text_lower or "sewage" in text_lower:
        category = "Drain Blockage"
    elif "heat" in text_lower:
        category = "Heat Hazard"
    else:
        category = "Other"

    # Priority detection
    if any(word in text_lower for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason field
    reason = f"Detected keywords from text: {text[:50]}"

    # Flag ambiguous cases
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return category, priority, reason, flag

def batch_classify(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            complaint = row.get("complaint", "")
            category, priority, reason, flag = classify_complaint(complaint)

            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag

            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
