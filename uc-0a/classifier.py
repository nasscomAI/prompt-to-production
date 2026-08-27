"""
UC-0A — Complaint Classifier
Implemented using RICE method logic for robust citizen complaint triage.
"""
import argparse
import csv
import os
import re

# Classification Schema Constants
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "crater"],
    "Flooding": ["flood", "waterlogging", "submerged", "excessive water"],
    "Streetlight": ["light", "dark", "lamp", "bulb"],
    "Waste": ["garbage", "trash", "waste", "dump", "litter"],
    "Noise": ["loud", "noise", "music", "sound", "volume"],
    "Heritage Damage": ["monument", "statue", "heritage", "historic", "ancient"],
    "Heat Hazard": ["heat", "hot", "sun", "shade", "burning"],
    "Drain Blockage": ["drain", "sewage", "clog", "gutter"],
    "Road Damage": ["crack", "asphalt", "broken road", "pavement"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based keyword matching.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").lower()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in description for kw in keywords):
            category = cat
            break
            
    # 2. Determine Priority
    priority = "Standard"
    if any(kw in description for kw in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif category in ["Noise", "Waste"]:
        priority = "Low"

    # 3. Generate Reason (Simplified citation logic)
    # Find the keyword that triggered the category
    found_kw = "relevant keywords"
    if category != "Other":
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in description:
                found_kw = f"'{kw}'"
                break
    
    reason = f"Classified as {category} because the description mentions {found_kw}."

    # 4. Set Flag
    flag = ""
    if category == "Other":
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
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if not results:
            print("No results to write.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
