"""
UC-0A — Complaint Classifier
Implementation based on RICE (agents.md) and skills.md.
"""
import argparse
import csv
import re
import os

# Classification Schema Constants
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_TRIGGERS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "deep hole", "crater", "sinkhole"],
    "Flooding": ["flood", "water", "standing water", "inundation", "puddle"],
    "Streetlight": ["light", "lamp", "dark", "bulb", "streetlight"],
    "Waste": ["trash", "garbage", "rubbish", "litter", "dump", "bin"],
    "Noise": ["noise", "loud", "sound", "barking", "music", "party"],
    "Road Damage": ["crack", "road surface", "pavement", "asphalt", "damage"],
    "Heritage Damage": ["heritage", "monument", "statue", "historical", "museum", "landmark"],
    "Heat Hazard": ["heat", "hot", "sun", "melting", "temperature"],
    "Drain Blockage": ["drain", "sewer", "clog", "blockage", "gutter", "pipe"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    if not description or description.strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description prevents classification.",
            "flag": "NEEDS_REVIEW"
        }

    # Determine Category
    category = "Other"
    found_keywords = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_keywords.append(kw)
                break
        if category != "Other":
            break

    # Determine Priority (Triggering Enforcement Rule)
    priority = "Standard"
    urgent_found = []
    for trigger in URGENT_TRIGGERS:
        if trigger in description:
            priority = "Urgent"
            urgent_found.append(trigger)
    
    # Reason sentence as per Enforcement (citational)
    if priority == "Urgent":
        reason = f"Classified as {category} because description mentions '{found_keywords[0] if found_keywords else 'problem'}'; upgraded to Urgent due to '{urgent_found[0]}'."
    elif category == "Other":
        reason = "No specific category keywords found in description."
    else:
        reason = f"Classified as {category} based on the presence of the word '{found_keywords[0]}'."

    # Flag Condition
    flag = ""
    if category == "Other" or description.strip().endswith("?"):
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write to output CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    # Merge original row with classification results
                    results.append(classification)
                except Exception as e:
                    print(f"Skipping bad row {row.get('complaint_id', 'unknown')}: {e}")

        if not results:
            print("No valid rows processed.")
            return

        # Write results to CSV
        output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
