"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    # Priority keywords enforcement
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    matched_severity = []
    
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            matched_severity.append(kw)

    # Categories logic mapping
    category_map = {
        "Pothole": ["pothole", "hole", "crater"],
        "Flooding": ["flood", "waterlogging", "submerged"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["waste", "garbage", "trash", "dead animal"],
        "Noise": ["noise", "loud", "music"],
        "Road Damage": ["crack", "road surface", "broken road", "broken tiles", "broken"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "sun", "burning"],
        "Drain Blockage": ["drain", "blocked", "sewer"],
    }

    matched_categories = []
    matched_category_kws = []
    
    for cat, kws in category_map.items():
        for kw in kws:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_category_kws.append(kw)

    flag = ""
    # Ambiguity Check Enforcement
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The category is genuinely ambiguous because no recognizable keywords were found."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"The category is genuinely ambiguous because multiple indicators ({', '.join(matched_categories)}) were found."
    else:
        category = matched_categories[0]
        cat_kw = matched_category_kws[0] if matched_category_kws else 'issue'
        if priority == "Urgent":
            sev_kw = matched_severity[0]
            reason = f"This is classified as {category} with Urgent priority due to citing the word '{cat_kw}' along with severity indicator '{sev_kw}'."
        else:
            reason = f"This is classified as {category} securely because the specific word '{cat_kw}' is mentioned in the description."

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
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Execute skill
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                    continue
    except FileNotFoundError:
        print(f"Failed to read input file: {input_path}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            if results:
                fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
