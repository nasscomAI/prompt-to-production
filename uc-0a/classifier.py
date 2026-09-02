"""
UC-0A — Complaint Classifier
Implementation adhering strictly to RICE -> agents.md -> skills.md rules.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAPPINGS = {
    "Pothole": ["pothole", "crater", "hole in road"],
    "Flooding": ["flood", "waterlogging", "submerged", "stagnant water"],
    "Streetlight": ["streetlight", "lamp", "dark street", "light bulb", "light"],
    "Waste": ["garbage", "trash", "waste", "dumping", "litter", "bin"],
    "Noise": ["loud", "noise", "speaker", "music", "honking"],
    "Road Damage": ["road damage", "asphalt", "cracked road", "broken road", "tar"],
    "Heritage Damage": ["heritage", "monument", "statue", "old fort", "ancient"],
    "Heat Hazard": ["heat", "sunstroke", "extreme heat", "warmth"],
    "Drain Blockage": ["drain", "sewage", "gutter", "clogged", "overflowing drain"]
}

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", row.get("id", "UNKNOWN"))
    description = row.get("description", row.get("complaint", "")).strip()
    desc_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description text.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    matched_category = "Other"
    matched_keyword = ""

    for category, keywords in CATEGORY_MAPPINGS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_category = category
                matched_keyword = kw
                break
        if matched_category != "Other":
            break

    # 2. Determine Priority & Trigger Keywords
    urgent_found = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if urgent_found:
        priority = "Urgent"
        priority_reason = f"contains urgent trigger word '{urgent_found[0]}'"
    else:
        priority = "Standard"
        priority_reason = "no urgent safety triggers detected"

    # 3. Formulate Reason
    if matched_category != "Other":
        reason = f"Classified as {matched_category} because description cites '{matched_keyword}' and {priority_reason}."
        flag = ""
    else:
        reason = f"Category ambiguous from text alone; {priority_reason}."
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified_row = classify_complaint(row)
                # Keep original row data + append new schema fields
                combined_row = {**row, **classified_row}
                results.append(combined_row)
            except Exception as e:
                # Failure resilience rule
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    if results:
        fieldnames = list(results[0].keys())
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    print(f"Successfully processed {len(results)} rows into '{output_path}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)