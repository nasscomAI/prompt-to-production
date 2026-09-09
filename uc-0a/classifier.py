"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "potholes"],
    "Flooding": ["flooding", "waterlogging", "waterlogged", "submerged", "overflow"],
    "Streetlight": ["streetlight", "street light", "dark", "lamp", "pole"],
    "Waste": ["garbage", "trash", "waste", "dump", "debris", "litter", "rubbish"],
    "Noise": ["noise", "loudspeaker", "music", "loud", "sound"],
    "Road Damage": ["road crack", "caved in", "asphalt", "broken road", "tarmac", "surface damaged"],
    "Heritage Damage": ["monument", "heritage", "statue", "historical", "fort"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "no shade"],
    "Drain Blockage": ["drain", "drainage", "gutter", "sewage", "clogged drain", "blocked drain"]
}


def classify_complaint(text: str):
    lower_text = text.lower()

    # Determine Priority
    found_severe = [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', lower_text)]
    if found_severe:
        priority = "Urgent"
        severe_reason = f"Contains severity trigger word '{found_severe[0]}'"
    else:
        priority = "Standard"
        severe_reason = "Standard civic grievance"

    # Match Categories
    matched_cats = []
    matched_terms = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        found = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', lower_text)]
        if found:
            matched_cats.append(cat)
            matched_terms[cat] = found[0]

    flag = ""
    if len(matched_cats) == 1:
        category = matched_cats[0]
        keyword = matched_terms[category]
        reason = f"Classified as {category} based on the phrase '{keyword}' with {severe_reason.lower()}."
    elif len(matched_cats) > 1:
        category = matched_cats[0]
        flag = "NEEDS_REVIEW"
        reason = f"Multiple issues detected ('{matched_terms[matched_cats[0]]}', '{matched_terms[matched_cats[1]]}'); flagged for review."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Grievance details are ambiguous and lack explicit category keywords; flagged for review."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_file: str, output_file: str):
    in_path = Path(input_file)
    if not in_path.exists():
        sys.exit(f"Error: Input file '{input_file}' not found.")

    rows = []
    with open(in_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])

        # Add required columns if not present
        for col in ["category", "priority", "reason", "flag"]:
            if col not in fieldnames:
                fieldnames.append(col)

        for row in reader:
            desc = row.get("description", "") or row.get("complaint", "") or row.get("text", "")
            classification = classify_complaint(desc)
            row.update(classification)
            rows.append(row)

    out_path = Path(output_file)
    with open(out_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully processed {len(rows)} records into: {out_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Classify citizen complaints.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
