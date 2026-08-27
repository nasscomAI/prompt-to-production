"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic derived from agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Taxonomy Mapping (Categories)
    category = "Other"
    found_keyword = ""
    
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water", "rain", "underpass flooded"],
        "Streetlight": [" streetlight", "light", "flickering", "dark"],
        "Waste": ["garbage", "trash", "waste", "bins", "smell", "animal"],
        "Noise": ["noise", "music", "loud", "midnight"],
        "Road Damage": ["cracked", "sinking", "tiles", "road surface", "footpath"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sun", "exhaustion"],
        "Drain Blockage": ["drain", "manhole", "overflowing"]
    }

    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_keyword = kw
                break
        if category != "Other":
            break

    # 2. Priority Logic (Urgent Escalation)
    priority = "Standard"
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    found_urgent = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            found_urgent = kw
            break
    
    # 3. Reason Generation
    if category != "Other":
        reason = f"Categorized as {category} because the description mentions '{found_keyword}'."
    else:
        reason = "Categorized as Other as no specific municipal category keywords were identified."
    
    if priority == "Urgent":
        reason += f" Escalated to Urgent due to safety keyword: '{found_urgent}'."

    # 4. Ambiguity Flagging
    flag = ""
    if category == "Other" or not description:
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
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id')}: {e}")
                    # Minimal fallback for failed row
                    results.append({
                        "complaint_id": row.get("complaint_id", "Error"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return

    # Write output
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
