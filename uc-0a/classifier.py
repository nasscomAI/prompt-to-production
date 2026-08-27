"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on description.
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = "No description provided."
    flag = ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Category logic (Keyword based for this iteration)
    categories = {
        "Pothole": ["pothole", "cracked", "hole in road"],
        "Flooding": ["flood", "waterlogging", "inundation"],
        "Streetlight": ["streetlight", "dark", "street light", "lamp"],
        "Waste": ["garbage", "trash", "waste", "dump"],
        "Noise": ["noise", "loud", "sound", "music"],
        "Road Damage": ["road damage", "damaged road", "asphalt"],
        "Heritage Damage": ["heritage", "monument", "statue", "historical"],
        "Heat Hazard": ["heat", "hot", "shade", "sun"],
        "Drain Blockage": ["drain", "sewage", "clogged", "blocked drain"]
    }

    desc_lower = description.lower()
    found_category = False
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                reason = f"Classified as {cat} because the description contains '{kw}'."
                found_category = True
                break
        if found_category:
            break
    
    if not found_category:
        category = "Other"
        reason = "No specific category matched the description keywords."
        flag = "NEEDS_REVIEW"

    # 2. Priority logic
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            reason += f" Priority set to Urgent due to keyword '{kw}'."
            break
    
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
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Skipping malformed row {row.get('complaint_id', 'unknown')}: {e}")

        if not results:
            print("No data processed.")
            return

        keys = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
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

