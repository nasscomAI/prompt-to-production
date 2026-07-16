"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "bump in road"],
    "Flooding": ["flood", "flooding", "waterlogged", "water logging", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp post", "street lamp"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumping", "debris", "rubbish"],
    "Noise": ["noise", "loud", "honking", "noisy", "sound pollution", "disturbance"],
    "Road Damage": ["road damage", "damaged road", "broken road", "cracked road", "rough road"],
    "Heritage Damage": ["heritage", "monument", "historical", "heritage site"],
    "Heat Hazard": ["heat", "heatwave", "hot", "extreme temperature", "heat stroke"],
    "Drain Blockage": ["drain", "drainage", "blockage", "clogged", "sewer", "blocked drain"],
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").strip()
    if not desc:
        raise ValueError("Description is empty or missing")

    desc_lower = desc.lower()

    matched_categories = []
    matched_keyword = None
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                # Keep track of the first matched keyword for the reason field
                if matched_keyword is None:
                    matched_keyword = kw
                break

    # If exactly one category is matched, classify under that category
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # 0 matches or multiple matches (ambiguous) -> Other, NEEDS_REVIEW
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority determination based on severity keywords
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # Reason generation: cite specific words from the description
    if category != "Other" and matched_keyword:
        reason = f"The description contains '{matched_keyword}', indicating a {category.lower()} complaint."
    else:
        words = desc.split()
        phrase = " ".join(words[:min(5, len(words))])
        if len(matched_categories) > 1:
            reason = f"The description matches multiple categories {matched_categories} starting with '{phrase}', indicating ambiguity."
        else:
            reason = f"The description reads '{phrase}' but does not clearly match a known category."

    complaint_id = row.get("complaint_id", "")

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                print(f"Warning: row {i} skipped — {e}")

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
