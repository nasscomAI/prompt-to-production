"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    desc_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent",
            "reason": "Missing description text.",
            "flag": "NEEDS_REVIEW"
        }

    flag = ""
    
    # 1. Determine Category (strictly within ALLOWED_CATEGORIES)
    if "heritage" in desc_lower or "tourist" in desc_lower and "waste" in desc_lower:
        category = "Heritage Damage" if "heritage" in desc_lower and "damage" in desc_lower else "Waste"
    elif "pothole" in desc_lower:
        category = "Pothole"
    elif "flooded" in desc_lower or "flooding" in desc_lower or "floods" in desc_lower:
        category = "Flooding"
    elif "drain" in desc_lower or "dengue" in desc_lower:
        category = "Drain Blockage"
    elif "garbage" in desc_lower or "waste" in desc_lower:
        category = "Waste"
    elif "drilling" in desc_lower or "noise" in desc_lower or "idling" in desc_lower:
        category = "Noise"
    elif "collapsed" in desc_lower or "crater" in desc_lower:
        category = "Road Damage"
    elif "lamp" in desc_lower or "dark" in desc_lower or "light" in desc_lower:
        category = "Streetlight"
    elif "heat" in desc_lower or "sun" in desc_lower:
        category = "Heat Hazard"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority (Urgent if severity keyword present)
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_severity:
        priority = "Urgent"
        cited_words = ", ".join([f"'{kw}'" for kw in matched_severity])
        reason = f"Classified as Urgent due to severity keyword(s) {cited_words} in description."
    else:
        days_open = int(row.get("days_open", 0)) if str(row.get("days_open", "")).isdigit() else 0
        if days_open > 10:
            priority = "Standard"
            reason = f"Classified as Standard priority based on routine complaint status open for {days_open} days."
        else:
            priority = "Low"
            reason = f"Classified as Low priority as no critical severity keywords were found in the description."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Urgent",
                    "reason": f"Processing error encountered: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                }
            results.append(classified)

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

