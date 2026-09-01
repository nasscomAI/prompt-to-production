"""
UC-0A — Complaint Classifier
Classifies complaint descriptions into category, priority, reason, and flag.
"""
import argparse
import csv

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "underpass flooded", "knee-deep", "abandoned", "flooding"],
    "Streetlight": ["streetlight", "lights out", "flickering", "sparky"],
    "Waste": ["garbage", "waste", "overflowing", "dumped", "decay", "dead animal"],
    "Noise": ["music", "midnight", "weeknights", "playing"],
    "Road Damage": ["cracked", "broken", "sinking", "collapsed", "crater", "road surface"],
    "Heritage Damage": ["heritage", "old city", "street"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain blocked", "blocked", "100% blocked"],
}


def _determine_category(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return "Other"


def _determine_priority(description: str) -> str:
    desc_lower = description.lower()
    found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found:
        return "Urgent"
    return "Standard"


def _determine_reason(description: str, category: str) -> str:
    keywords_by_category = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights"],
        "Waste": ["garbage", "waste"],
        "Noise": ["music"],
        "Road Damage": ["cracked"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked"],
        "Other": [],
    }
    relevant = keywords_by_category.get(category, [])
    found = [w for w in relevant if w in description.lower()]
    if found:
        return f"Detected {category.lower()} due to '{found[0]}' in description."
    return f"Classified as {category} based on description keywords."


def _determine_flag(category: str, description: str) -> str:
    desc_lower = description.lower()
    ambiguous_keywords = {"ambiguous", "uncertain", "general concern"}
    if category == "Other":
        return "NEEDS_REVIEW"
    for kw in ambiguous_keywords:
        if kw in desc_lower:
            return "NEEDS_REVIEW"
    return ""


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "")

    category = _determine_category(description)
    priority = _determine_priority(description)
    reason = _determine_reason(description, category)
    flag = _determine_flag(category, description)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    import os
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(input_path, "r", newline="", encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                writer.writerow({"complaint_id": row.get("complaint_id", ""), "category": "Other", "priority": "Standard", "reason": f"Error processing row: {e}", "flag": "NEEDS_REVIEW"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
