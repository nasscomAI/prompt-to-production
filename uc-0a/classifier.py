"""
UC-0A — Complaint Classifier
Implements the RICE enforcement rules from agents.md and the skill
patterns from skills.md to classify citizen complaints.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage",
    "Other",
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "flooded": "Flooding",
    "drain": "Drain Blockage",
    "drainage": "Drain Blockage",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "dead animal": "Waste",
    "noise": "Noise",
    "music": "Noise",
    "road damage": "Road Damage",
    "road surface": "Road Damage",
    "cracked": "Road Damage",
    "sinking": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "manhole": "Other",
    "footpath": "Other",
    "tile": "Other",
}


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").lower()
    full_text = (row.get("description") or "") + " " + (row.get("location") or "")
    full_text_lower = full_text.lower()

    category = "Other"
    matched_keyword = None
    for kw, cat in CATEGORY_KEYWORDS.items():
        if kw in description:
            matched_keyword = kw
            category = cat
            break

    has_urgent = any(kw in full_text_lower for kw in URGENT_KEYWORDS)
    if has_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"

    severity_words_found = [kw for kw in URGENT_KEYWORDS if kw in full_text_lower]
    if severity_words_found:
        reason = f"Description contains severity keywords: {', '.join(severity_words_found)}"
    elif matched_keyword:
        reason = f"Description mentions '{matched_keyword}' matching category '{category}'"
    else:
        reason = "No specific keywords matched; classified based on context"

    flag = ""
    if category == "Other" and not matched_keyword:
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if not row.get("complaint_id", "").strip():
                continue
            try:
                result = classify_complaint(row)
                rows.append(result)
            except Exception as e:
                rows.append({
                    "complaint_id": row.get("complaint_id", f"row_{i}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    if not rows:
        raise ValueError("No valid rows found in input file")

    with open(output_path, "w", newline="") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
