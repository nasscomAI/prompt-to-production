"""
UC-0A — Complaint Classifier
Implements RICE rules from agents.md and skills defined in skills.md.
"""
import argparse
import csv
import re
import os

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description text in complaint.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()

    # 1. Determine Priority via Severity Keywords
    is_urgent = any(re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) or kw in desc_lower for kw in SEVERITY_KEYWORDS)
    if is_urgent:
        priority = "Urgent"
    else:
        days_open = row.get("days_open", "0")
        try:
            days = int(days_open)
            priority = "Standard" if days < 15 else "Low"
        except ValueError:
            priority = "Standard"

    # 2. Determine Category strictly from ALLOWED_CATEGORIES
    category = "Other"
    flag = ""

    # Check categories using regex patterns with word boundaries
    if re.search(r'\b(pothole|potholes)\b', desc_lower):
        category = "Pothole"
    elif re.search(r'\b(waste|garbage|trash|bins|overflowing)\b', desc_lower):
        category = "Waste"
    elif re.search(r'\b(music|noise|loudspeaker|audible|sound)\b', desc_lower):
        category = "Noise"
    elif re.search(r'\b(unlit|lighting|streetlight|wiring|lamp)\b', desc_lower):
        category = "Streetlight"
    elif re.search(r'\b(heritage|ancient|step well|historic|monument)\b', desc_lower):
        category = "Heritage Damage"
    elif re.search(r'\b(heat|heatwave|44°c|45°c|52°c|temperature|full sun|melting)\b', desc_lower):
        category = "Heat Hazard"
    elif re.search(r'\b(flood|flooding|waterlogging|submerged)\b', desc_lower):
        category = "Flooding"
    elif re.search(r'\b(drain|drainage|sewer|clogged)\b', desc_lower):
        category = "Drain Blockage"
    elif re.search(r'\b(tarmac|paving|subsidence|road|divider|surface|asphalt)\b', desc_lower):
        category = "Road Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # If category is Other, set flag to NEEDS_REVIEW
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 3. Formulate Reason (citing specific words from description)
    first_sentence = desc.split(".")[0].strip() if "." in desc else desc
    reason = f"Classified based on description citing '{first_sentence}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, classifies each row, and writes output CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
