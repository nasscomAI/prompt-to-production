"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md specifications.
"""
import argparse
import csv
import os

# Taxonomy and priority rules
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based heuristics 
    that strictly follow the RICE enforcement rules.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Determine Category
    category = "Other"
    found_words = []
    
    if "pothole" in description:
        category = "Pothole"
        found_words.append("pothole")
    elif "flood" in description or "rain" in description:
        category = "Flooding"
        found_words.append("flood" if "flood" in description else "rain")
    elif "streetlight" in description or "lights out" in description:
        category = "Streetlight"
        found_words.append("streetlight" if "streetlight" in description else "lights out")
    elif "garbage" in description or "waste" in description or "dumped" in description or "animal" in description:
        category = "Waste"
        if "garbage" in description: found_words.append("garbage")
        if "waste" in description: found_words.append("waste")
        if "dumped" in description: found_words.append("dumped")
        if "animal" in description: found_words.append("dead animal")
    elif "noise" in description or "music" in description:
        category = "Noise"
        found_words.append("noise" if "noise" in description else "music")
    elif "drain" in description or "manhole" in description:
        category = "Drain Blockage"
        found_words.append("drain" if "drain" in description else "manhole")
    elif "heritage" in description:
        category = "Heritage Damage"
        found_words.append("heritage")
    elif "heat" in description:
        category = "Heat Hazard"
        found_words.append("heat")
    elif "road" in description or "footpath" in description or "tiles" in description:
        category = "Road Damage"
        if "road" in description: found_words.append("road")
        if "footpath" in description: found_words.append("footpath")
        if "tiles" in description: found_words.append("tiles")
        if "crack" in description: found_words.append("cracked")
        if "sink" in description: found_words.append("sinking")
    
    # 2. Determine Priority
    priority = "Low"
    triggered_keywords = [word for word in URGENT_KEYWORDS if word in description]
    
    if triggered_keywords:
        priority = "Urgent"
    elif any(word in description for word in ["risk", "safety", "danger", "stranded"]):
        priority = "Standard"
    else:
        priority = "Standard" # Defaulting to Standard if not Urgent but valid category

    # 3. Generate Reason
    if found_words:
        reason = f"Classified as {category} because the description mentions '{', '.join(found_words)}'."
    else:
        reason = "Could not determine a specific category from the description."

    # 4. Set Flag
    flag = ""
    if category == "Other" or not found_words:
        flag = "NEEDS_REVIEW"
    elif len(found_words) > 1 and category == "Other": # Genuinely ambiguous
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
                classified = classify_complaint(row)
                results.append(classified)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
