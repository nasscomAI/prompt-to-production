"""
UC-0A — Complaint Classifier
Built from agents.md (RICE) and skills.md via the CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# category -> keywords that indicate that category in the description
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding"],
    "Streetlight": ["streetlight", "street light", "street lamp"],
    "Waste": ["garbage", "waste", "trash"],
    "Noise": ["noise", "drilling", "idling", "engines on", "loud"],
    "Road Damage": ["road collapsed", "crater", "road damage"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave"],
    "Drain Blockage": ["drain blocked", "drain completely blocked", "stormwater drain", "main drain"],
}


def _matched_categories(description: str) -> list[str]:
    text = description.lower()
    matches = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matches.append(category)
                break
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "no description provided",
            "flag": "NEEDS_REVIEW",
        }

    text_lower = description.lower()

    matched = _matched_categories(description)
    if len(matched) == 1:
        category = matched[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    hit_keyword = next((kw for kw in URGENT_KEYWORDS if kw in text_lower), None)
    priority = "Urgent" if hit_keyword else "Standard"

    if hit_keyword:
        match = re.search(re.escape(hit_keyword), description, re.IGNORECASE)
        quoted = match.group(0) if match else hit_keyword
        reason = f"Contains severity keyword '{quoted}' in description."
    elif matched:
        reason = f"Description matches '{matched[0]}' based on wording in: \"{description}\"."
    else:
        reason = f"No category keyword matched description: \"{description}\"."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "row could not be processed",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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
