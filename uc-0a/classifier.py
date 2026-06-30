"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and flag.
"""
import argparse
import csv
import re
import sys


URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "potholes", "crater", "craters", "hole in the road", "holes in the road"]),
    ("Flooding", ["flood", "flooded", "flooding", "floods", "waterlogged", "water logging", "stagnant water", "submerged"]),
    ("Streetlight", ["streetlight", "streetlights", "street light", "lamp post", "lamp", "light not working"]),
    ("Waste", ["garbage", "trash", "waste", "litter", "rubbish", "dump", "refuse", "debris", "overflowing bin"]),
    ("Noise", ["noise", "loud", "honking", "blaring", "music", "wedding", "party", "sound pollution"]),
    ("Road Damage", ["road damage", "damaged road", "broken road", "cracked road", "rough road", "road surface", "deteriorated road"]),
    ("Heritage Damage", ["heritage", "monument", "historical site", "ancient", "archaeological"]),
    ("Heat Hazard", ["heat", "hot", "sunstroke", "scorching", "heatwave", "extreme temperature"]),
    ("Drain Blockage", ["drain", "sewer", "blocked drain", "choked drain", "clogged", "manhole", "drainage"]),
]


def _find_matching_keyword(text: str, keywords: list) -> str | None:
    for kw in keywords:
        m = re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)
        if m:
            return m.group()
    return None


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = []
    for cat, keywords in CATEGORY_RULES:
        if _find_matching_keyword(description, keywords):
            matched_categories.append(cat)

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority
    urgent_word = _find_matching_keyword(description, URGENT_KEYWORDS)
    if urgent_word:
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # Reason — one sentence citing specific words from the description
    if flag == "" and category != "Other":
        for cat, keywords in CATEGORY_RULES:
            if cat == category:
                match = _find_matching_keyword(description, keywords)
                if match:
                    reason = f"The complaint mentions '{match}' which indicates {category.lower()}."
                else:
                    reason = f"The complaint relates to {category.lower()}."
                break
    else:
        match = _find_matching_keyword(description, URGENT_KEYWORDS)
        if match:
            reason = f"The complaint mentions '{match}' which requires urgent attention."
        else:
            words = [w for w in description.split() if len(w) > 3]
            if words:
                reason = f"The complaint contains '{words[0]}' but does not clearly match any single category."
            else:
                reason = "The complaint description is insufficient for classification."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                print(f"Warning: Failed to classify row {i}: {e}", file=sys.stderr)

    if not results:
        print("Warning: No rows were classified. Writing empty output with headers.", file=sys.stderr)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
