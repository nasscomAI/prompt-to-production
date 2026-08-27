"""
UC-0A — Complaint Classifier
Rule-based implementation built to simulate a perfect CRAFT workflow agent.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogged", "water logging"],
    "Streetlight": ["streetlight", "light", "dark"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump"],
    "Noise": ["noise", "loud", "music", "party"],
    "Road Damage": ["damage", "crack", "broken road", "cave-in", "caved in"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "sun", "wave"],
    "Drain Blockage": ["drain", "block", "clog", "sewer"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Priority
    priority = "Standard"
    matched_severity = []
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', desc):
            priority = "Urgent"
            matched_severity.append(keyword)

    # 2. Determine Category
    category = "Other"
    matched_cat_word = ""
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc):
                category = cat
                matched_cat_word = kw
                break
        if category != "Other":
            break
            
    # 3. Handle Flags and Reason
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        if priority == "Urgent":
            reason = f"Marked for review because category is ambiguous, but marked Urgent because it mentions '{matched_severity[0]}'."
        else:
            reason = "Marked for review because the description is ambiguous and lacks known category keywords."
    else:
        if priority == "Urgent":
            reason = f"Classified as {category} and Urgent because the description mentions '{matched_cat_word}' and '{matched_severity[0]}'."
        else:
            reason = f"Classified as {category} because the description mentions '{matched_cat_word}'."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if not row.get("complaint_id") or not row.get("description"):
                continue  # skip bad rows
            
            classified = classify_complaint(row)
            results.append(classified)
            
    if not results:
        print("No valid rows found to process.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
