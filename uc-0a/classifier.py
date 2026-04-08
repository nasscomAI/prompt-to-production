"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORY_LIST = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
PRIORITY_LIST = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "")
    result = {"category": "", "priority": "", "reason": "", "flag": ""}
    if not description or not isinstance(description, str):
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = "Missing or invalid description"
        return result

    # Category classification (simple keyword matching, fallback to Other)
    category = None
    desc_lower = description.lower()
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging"],
        "Streetlight": ["streetlight", "lamp", "light"],
        "Waste": ["waste", "garbage", "trash", "dump"],
        "Noise": ["noise", "loud", "sound"],
        "Road Damage": ["road damage", "crack", "uneven", "broken road"],
        "Heritage Damage": ["heritage", "monument", "historic", "damage"],
        "Heat Hazard": ["heat", "hot", "temperature"],
        "Drain Blockage": ["drain", "block", "clog", "sewage"],
    }
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                break
        if category:
            break
    if not category:
        category = "Other"
    result["category"] = category

    # Priority classification
    if any(kw in desc_lower for kw in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"
    result["priority"] = priority

    # Reason: must cite specific words from description
    cited = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            cited = kw
            break
    if cited:
        result["reason"] = f"Contains severity keyword: '{cited}'"
    else:
        # Use first matched category keyword as reason
        for kw in category_keywords.get(category, []):
            if kw in desc_lower:
                result["reason"] = f"Mentions '{kw}'"
                break
        if not result["reason"]:
            result["reason"] = "No specific keyword found"

    # Flag: set NEEDS_REVIEW if ambiguous (e.g., category is Other)
    if category == "Other":
        result["flag"] = "NEEDS_REVIEW"
    else:
        result["flag"] = ""
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"] if reader.fieldnames else ["description", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            try:
                result = classify_complaint(row)
                row.update(result)
            except Exception as e:
                row.update({"category": "", "priority": "", "reason": f"Error: {e}", "flag": "NEEDS_REVIEW"})
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
