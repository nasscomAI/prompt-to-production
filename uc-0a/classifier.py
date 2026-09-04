"""
UC-0A — Complaint Classifier
RICE + CRAFT implementation for single and batch complaint classification.
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
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using exact rules from agents.md / skills.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    # Category matching logic
    category = "Other"
    flag = ""
    
    # Check matching keywords/patterns for strict taxonomy
    if re.search(r'\bpothole\b|\bpotholes\b', desc_lower):
        category = "Pothole"
    elif re.search(r'\bflood|\bflooded|\bflooding\b|\binundat', desc_lower):
        category = "Flooding"
    elif re.search(r'\bdrain\b|\bdrainage\b|\bsewer\b|\bchoked drain\b|\bblocked drain\b', desc_lower):
        category = "Drain Blockage"
    elif re.search(r'\bstreetlight\b|\bstreetlights\b|\blights out\b|\blight\b', desc_lower):
        category = "Streetlight"
    elif re.search(r'\bgarbage\b|\bwaste\b|\bdumped\b|\bbins\b|\bdead animal\b', desc_lower):
        category = "Waste"
    elif re.search(r'\bmusic\b|\bnoise\b|\bloud\b|\bsound\b', desc_lower):
        category = "Noise"
    elif re.search(r'\bheritage\b', desc_lower):
        category = "Heritage Damage"
    elif re.search(r'\bheat\b|\bsunstroke\b|\bheatwave\b', desc_lower):
        category = "Heat Hazard"
    elif re.search(r'\broad\b|\bfootpath\b|\btiles\b|\bsinking\b|\bcracked\b', desc_lower):
        category = "Road Damage"

    # Heritage street light case check: ambiguation flag if multiple categories apply
    if "heritage" in desc_lower and ("light" in desc_lower or "lights" in desc_lower):
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"

    # Priority determination
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_severity:
        priority = "Urgent"
        reason = f"Contains severity keyword '{matched_severity[0]}' in description."
    else:
        # Check days open or general default
        days_open = int(row.get("days_open", 0)) if row.get("days_open", "0").isdigit() else 0
        if days_open > 14:
            priority = "Standard"
            reason = f"Complaint open for {days_open} days."
        else:
            priority = "Standard"
            reason = f"Standard complaint description cited: '{desc[:50]}...'."

    # Final enforcement validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
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
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
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
