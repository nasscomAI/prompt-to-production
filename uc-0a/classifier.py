"""
UC-0A complaint classifier.
"""
import argparse
import csv

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
    "Other",
]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flooded", "floods", "flooding", "underpass flooded"]),
    ("Streetlight", ["streetlight", "streetlights", "lights out", "flickering", "sparking"]),
    ("Waste", ["garbage", "waste", "bins", "dead animal", "dumped"]),
    ("Noise", ["music past midnight", "playing music", "noise"]),
    ("Road Damage", ["road surface cracked", "sinking", "footpath", "tiles broken", "manhole cover missing"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "heatwave"]),
    ("Drain Blockage", ["drain blocked", "drainage blocked", "manhole blocked"]),
]
LOW_PRIORITY_KEYWORDS = ["flickering"]


def classify_complaint(row: dict) -> dict:
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    text = description.lower()

    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            matched_categories.append(category)

    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(set(matched_categories)) > 1:
        ordered = []
        for category in matched_categories:
            if category not in ordered:
                ordered.append(category)
        if ordered == ["Flooding", "Drain Blockage"]:
            category = "Drain Blockage"
            flag = ""
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
    else:
        category = matched_categories[0]
        flag = ""

    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif any(keyword in text for keyword in LOW_PRIORITY_KEYWORDS):
        priority = "Low"
    else:
        priority = "Standard"

    reason = f'Category set to {category} because description says "{description}"; priority set to {priority} from those same words.'

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f'Could not classify because "{exc}".',
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
