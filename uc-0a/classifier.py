"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on keywords and safety rules.
    """
    desc = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', 'Unknown')
    
    # 1. Determine Category
    category = "Other"
    flag = ""
    
    if "pothole" in desc:
        category = "Pothole"
    elif "flood" in desc or "rain" in desc:
        category = "Flooding"
    elif "streetlight" in desc or "lights" in desc or "dark" in desc:
        if "heritage" in desc:
            category = "Heritage Damage"
        else:
            category = "Streetlight"
    elif "garbage" in desc or "waste" in desc or "dumped" in desc or "dead animal" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
    elif "road" in desc and ("crack" in desc or "sink" in desc or "damage" in desc):
        category = "Road Damage"
    elif "drain" in desc or "sewage" in desc:
        category = "Drain Blockage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    if any(word in desc for word in severity_keywords):
        priority = "Urgent"
    elif "low" in desc or "minor" in desc:
        priority = "Low"

    # 3. Generate Reason (One sentence, cite words)
    # Simple logic to find the keyword that triggered the category/priority
    trigger_words = []
    for word in severity_keywords:
        if word in desc:
            trigger_words.append(word)
    
    reason = f"Classified as {category} because description mentions '{category.lower()}'; prioritized as {priority} due to words like '{', '.join(trigger_words) if trigger_words else 'none'}'. "
    # Ensure exactly one sentence (very simple)
    reason = reason.strip()

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
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get('complaint_id', 'Error'),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    if not results:
        print("No results to write.")
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
