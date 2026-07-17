"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import re

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "road hole", "road damage"],
    "Flooding": ["flood", "flooding", "waterlogged", "water logging", "overflow"],
    "Streetlight": ["streetlight", "street light", "lamp", "light not working", "no light"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "litter", "refuse"],
    "Noise": ["noise", "loud", "sound", "honking", "music", "disturbance"],
    "Road Damage": ["road damage", "crack", "broken road", "road condition", "asphalt"],
    "Heritage Damage": ["heritage", "monument", "historical", "temple", "archaeological"],
    "Heat Hazard": ["heat", "hot", "temperature", "sunstroke", "heatwave"],
    "Drain Blockage": ["drain", "blocked", "blockage", "clogged", "sewer", "sewage"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""

    # Error handling: null/empty description
    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Category classification
    category = "Other"
    matched_categories = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                break

    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other"

    # Priority classification
    priority = "Standard"
    if any(kw in desc_lower for kw in SEVERITY_KEYWORDS):
        priority = "Urgent"

    # Reason: cite specific words from description
    reason = f"Description mentions: {description.strip()[:80]}"

    # Flag: ambiguous if category is Other or multiple matches
    flag = "NEEDS_REVIEW" if category == "Other" or len(matched_categories) > 1 else ""

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
    Handles nulls, bad rows, and continues on failure.
    """
    output_rows = []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    output_rows.append(result)
                except Exception as e:
                    output_rows.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
