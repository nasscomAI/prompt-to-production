"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Define allowed categories and keywords
    categories = {
        "Pothole": ["pothole", "cracked", "sinking"],
        "Flooding": ["flood", "water", "drain", "rain"],
        "Streetlight": ["light", "dark", "flicker", "spark"],
        "Waste": ["garbage", "waste", "smell", "dumped", "animal"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road surface", "footpath", "tiles"],
        "Heritage Damage": ["heritage", "old city"],
        "Heat Hazard": ["heat", "sun", "hot"],
    }
    
    # 2. Match Category
    matched_category = "Other"
    for cat, keywords in categories.items():
        if any(kw in desc for kw in keywords):
            matched_category = cat
            break
            
    # 3. Determine Priority (Severity Keywords)
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse', 'risk']
    priority = "Standard"
    if any(kw in desc for kw in severity_keywords):
        priority = "Urgent"
    elif "light out" in desc or "dark" in desc:
        priority = "Standard" # Default
    
    # 4. Generate Reason
    # Find the specific word that triggered the classification for the reason
    reason = f"Classified as {matched_category} based on description."
    for kw in severity_keywords:
        if kw in desc:
            reason = f"Urgent priority due to mention of '{kw}'."
            break

    # 5. Handle Flags
    flag = ""
    if matched_category == "Other" or not desc:
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": matched_category,
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
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    if not results:
        print("No data to process.")
        return

    keys = results[0].keys()
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

