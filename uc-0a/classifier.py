"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Allowed categories from README
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that must trigger Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Category Mapping with Triggered Word Tracking
    category_to_keywords = {
        "Pothole": ["pothole", "pit"],
        "Drain Blockage": ["drain", "sewage", "gutter", "manhole"],
        "Flooding": ["flood", "waterlogging", "submerged", "water"],
        "Streetlight": ["streetlight", "lamp", "lights", "dark"],
        "Waste": ["waste", "garbage", "trash", "dump", "smell"],
        "Noise": ["noise", "loud", "sound", "music"],
        "Road Damage": ["road surface", "crack", "broken road", "asphalt", "tiles"],
        "Heritage Damage": ["monument", "statue", "temple", "heritage damage"], # specialized
        "Heat Hazard": ["heat", "sun", "hot", "thermal"]
    }

    category = "Other"
    trigger_word = ""
    for cat, kws in category_to_keywords.items():
        for kw in kws:
            if kw in description:
                category = cat
                trigger_word = kw
                break
        if category != "Other":
            break

    # 2. Priority Logic (Severity keywords)
    priority = "Standard"
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    
    # 3. Reason Construction
    if found_severity:
        priority = "Urgent"
        # Prioritize citing the severity word
        reason = f"Priority set to Urgent due to the mention of '{found_severity[0]}' in the report."
    elif category != "Other":
        reason = f"Classified as {category} because the description contains the keyword '{trigger_word}'."
    else:
        reason = "Classified as Other because the description did not match any specific category keywords."

    # 4. Ambiguitiy Flag
    # Set NEEDS_REVIEW if Other OR if it's a heritage mention without "Damage" specifically
    flag = ""
    if category == "Other" or ("heritage" in description and "damage" not in description):
        flag = "NEEDS_REVIEW"
        if category == "Other":
            reason = f"Flagged for review; first word '{description.split()[0] if description.split() else 'none'}' suggests an unmapped category."

    # Final validation for "category names must match exactly"
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    # Ensure reason is single sentence
    reason = reason.strip()
    if not reason.endswith('.'):
        reason += "."

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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if not row: continue
                try:
                    results.append(classify_complaint(row))
                except Exception:
                    continue

        if not results:
            return

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
