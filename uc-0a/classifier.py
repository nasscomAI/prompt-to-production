"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "underpass flood"],
    "Streetlight": ["streetlight", "street light", "lamp", "lighting"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "overflow", "pile", "dump"],
    "Noise": ["noise", "noisy", "drilling", "loud", "idling", "engine"],
    "Road Damage": ["road collapse", "road damage", "crater", "road broken", "road caved"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain blocked", "drain blockage", "drain clog", "stormwater drain", "main drain"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint into category, priority, reason, and flag based on exact schema.
    """
    description = row.get("description", "").lower().strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Invalid input - no description provided.",
            "flag": "NEEDS_REVIEW",
        }

    # Compute category scores
    category_scores = {cat: 0 for cat in ALLOWED_CATEGORIES if cat != "Other"}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            category_scores[cat] += description.count(kw)

    # Special boost for Heritage Damage if waste-related
    if "heritage" in description and any(w in description for w in ["garbage", "waste", "trash", "rubbish"]):
        category_scores["Heritage Damage"] += 2

    max_score = max(category_scores.values())
    top_categories = [cat for cat, score in category_scores.items() if score == max_score]
    is_tie = len(top_categories) > 1

    category = top_categories[0] if not is_tie else "Other"
    matched_keyword = ', '.join(top_categories[0].lower() for _ in range(min(3, max_score))) if max_score > 0 and not is_tie else "no clear match"

    # Determine priority (Urgent only on severity)
    severity_found = [sk for sk in SEVERITY_KEYWORDS if sk in description]
    priority = "Urgent" if severity_found else "Low"

    # Determine flag
    flag = "NEEDS_REVIEW" if is_tie else ""
    if max_score == 0:
        flag = "NEEDS_REVIEW"

    # Build reason (one sentence citing specifics)
    if is_tie:
        reason = f"Ambiguous: tie between {', '.join(top_categories)} ({max_score})."
    elif severity_found:
        reason = f"{category} citing '{matched_keyword}'; Urgent ('{', '.join(severity_found)}')."
    elif max_score > 0:
        reason = f"{category} citing '{matched_keyword}'."
    else:
        reason = "No keywords matched."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
