"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Taxonomy and Keyword Mapping (from agents.md)
CATEGORY_MAPPING = {
    "Pothole": ["pothole", "crater", "manhole"],
    "Flooding": ["flood", "water", "logging", "stagnation", "rain"],
    "Streetlight": ["streetlight", "light", "bulb", "dark", "flickering"],
    "Waste": ["garbage", "trash", "waste", "bin", "dump", "animal"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road surface", "cracked", "sinking", "pavement", "tiles", "broken"],
    "Heritage Damage": ["heritage", "monument", "statue", "old city"],
    "Heat Hazard": ["heat", "hot", "sunstroke", "thermal"],
    "Drain Blockage": ["drain", "sewage", "gutter", "overflow"]
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with original keys + category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category (Enforcement Rule 1)
    detected_category = "Other"
    reason_snippet = ""
    for category, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in description:
                detected_category = category
                reason_snippet = f"The description mentions '{kw}'"
                break
        if detected_category != "Other":
            break

    # 2. Determine Priority (Enforcement Rule 2)
    priority = "Standard"
    trigger_word = None
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            trigger_word = kw
            break
    
    if priority != "Urgent":
        # Additional logic for priority based on days_open or other factors if desired,
        # but RICE says specifically about severity keywords.
        priority = "Standard" # Default

    # 3. Handle Ambiguity (Enforcement Rule 4)
    flag = ""
    if detected_category == "Other" or not description:
        flag = "NEEDS_REVIEW"
        if not reason_snippet:
            reason_snippet = "Category could not be determined from the description text alone."
    
    # 4. Final Reason (Enforcement Rule 3) - cited words
    if priority == "Urgent":
        reason = f"{reason_snippet} and contains the severity keyword '{trigger_word}'."
    else:
        reason = f"{reason_snippet}."

    row["category"] = detected_category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    
    return row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            for row in reader:
                classified_row = classify_complaint(row)
                results.append(classified_row)
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
