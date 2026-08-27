"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

URGENCY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Heritage Damage": ["heritage", "monument", "temple damage", "historical", "plaques", "heritage structure"],
    "Drain Blockage": ["drain", "drainage", "sewer", "clogged drain", "blocked drain", "overflowing drain", "sewage"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "litter", "overflowing bin", "bin full", "scattered waste"],
    "Flooding": ["flood", "flooding", "waterlogged", "waterlogging", "submerged", "rainwater", "flash flood", "lake overflow", "overflowed onto road", "overflowed"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamppost", "light not working", "no light", "streetlight out"],
    "Noise": ["noise", "loud", "loudspeaker", "honking", "construction noise", "dj ", "music"],
    "Pothole": ["pothole", "potholes", "road hole", "road sink"],
    "Road Damage": ["road damage", "broken road", "crack", "cracks", "road surface", "asphalt", "tarmac", "manhole cover missing", "road crack"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "dehydration", "exposed sun", "scorching", "heat hazard"],
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""

    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": "",
    }

    desc_lower = description.lower()

    if not description.strip():
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = "No description provided."
        return result

    # Category detection
    category = "Other"
    matched_keyword = ""
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keyword = kw
                break
        if category != "Other":
            break

    # Urgency detection
    urgency_word = ""
    for kw in URGENCY_KEYWORDS:
        if kw in desc_lower:
            urgency_word = kw
            break
    priority = "Urgent" if urgency_word else "Standard"

    # Reason: cite a specific word/phrase from the description
    if category == "Other":
        reason = f"Description does not clearly match a known category."
        flag = "NEEDS_REVIEW"
    else:
        reason = f"Contains reference to '{matched_keyword}'."
        flag = ""

    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    return result


def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row processing failed.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
