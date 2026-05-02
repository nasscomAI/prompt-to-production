import argparse
import csv
import re

# CORRECTED TAXONOMY - DO NOT CHANGE THESE STRINGS
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# CORRECTED URGENCY KEYWORDS
URGENCY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

# Updated Patterns to match the required categories
CATEGORY_PATTERNS = [
    ("Pothole", [r"pothole", r"hole"]),
    ("Flooding", [r"flood", r"waterlogging", r"water logging"]),
    ("Streetlight", [r"light", r"lamp", r"dark"]),
    ("Waste", [r"garbage", r"trash", r"waste", r"litter"]),
    ("Noise", [r"noise", r"loud", r"sound", r"speaker"]),
    ("Road Damage", [r"road", r"crack", r"broken"]),
    ("Drain Blockage", [r"drain", r"sewage", r"block"]),
]

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id") or row.get("id") or "0"
    desc = (row.get("description") or "").lower()

    # Default values
    category = "Other"
    priority = "Standard"
    reason = "Classified based on keywords."
    flag = ""

    # 1. Match Category
    for cat, patterns in CATEGORY_PATTERNS:
        if any(re.search(p, desc) for p in patterns):
            category = cat
            break
    
    if category == "Other": flag = "NEEDS_REVIEW"

    # 2. Check Urgency (Priority)
    if any(word in desc for word in URGENCY_KEYWORDS):
        priority = "Urgent"
    elif "low" in desc:
        priority = "Low"

    # 3. Create Reason
    reason = f"Identified as {category} with {priority} priority based on description."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(classify_complaint(row))
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Success! Generated {args.output}")
