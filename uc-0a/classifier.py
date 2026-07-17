"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "tyre damage", "tire damage"],
    "Flooding": ["flood", "flooded", "flooding", "knee-deep", "waterlogged", "water logging"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "dark at night", "lamp"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "overflowing bin", "dead animal", "dumped"],
    "Noise": ["noise", "music", "loud", "blaring", "midnight", "disturbance"],
    "Road Damage": ["cracked", "sinking", "road surface", "broken road", "footpath", "tiles broken"],
    "Heritage Damage": ["heritage", "old city", "historical"],
    "Heat Hazard": ["heat", "hot", "sunstroke", "dehydration", "extreme temperature"],
    "Drain Blockage": ["drain", "blocked drain", "sewer", "manhole", "overflowing drain"],
}


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty or unreadable description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            category = cat
            break

    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    matched_words = []
    all_keywords = {**CATEGORY_KEYWORDS}
    all_keywords["severity"] = SEVERITY_KEYWORDS
    for kw_list in all_keywords.values():
        for kw in kw_list:
            if kw in desc_lower:
                matched_words.append(kw)

    if matched_words:
        reason = f"Classification based on keywords: {', '.join(matched_words[:3])} found in description."
    else:
        reason = "No strong keyword match found; classified as Other."
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "description" not in reader.fieldnames:
                raise ValueError(f"Input CSV missing 'description' column. Found: {reader.fieldnames}")
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification failed: {str(e)}",
                "flag": "NEEDS_REVIEW",
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
