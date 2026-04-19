"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole in road"],
    "Flooding": ["flood", "waterlogging", "rain water", "submerged"],
    "Streetlight": ["light", "dark", "lamp", "street light"],
    "Waste": ["garbage", "trash", "waste", "dump", "plastic", "bin"],
    "Noise": ["noise", "loud", "sound", "music", "disturbance"],
    "Road Damage": ["road", "broken road", "surface", "pavement"],
    "Heritage Damage": ["heritage", "monument", "statue", "old building"],
    "Heat Hazard": ["heat", "hot", "sunstroke", "extreme temperature"],
    "Drain Blockage": ["drain", "sewage", "overflow", "gutter", "blockage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "Unknown")

    if not description or len(description) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or too short to classify.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # 1. Determine Category
    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            category = cat
            break
    
    # 2. Determine Priority
    priority = "Standard"
    urgent_trigger = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if urgent_trigger:
        priority = "Urgent"
    elif "low" in desc_lower or "minor" in desc_lower:
        priority = "Low"

    # 3. Generate Reason
    if priority == "Urgent":
        reason = f"Classified as Urgent because it mentions safety-critical terms like '{urgent_trigger[0]}'."
    elif category != "Other":
        reason = f"Classified as {category} based on the mention of related infrastructure issues."
    else:
        reason = "Classified as Other due to lack of specific infrastructure keywords."

    # 4. Set Flag
    flag = ""
    if category == "Other" or "not sure" in desc_lower or "unclear" in desc_lower:
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
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Warning: Failed to process row {row.get('complaint_id', 'unknown')}: {e}")
                    continue

        if not results:
            print("No data found in input file.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Critical Error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
