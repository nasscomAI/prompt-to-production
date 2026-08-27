"""
UC-0A — Complaint Classifier
Classifies citizen complaints into category, priority, reason, and flag.
"""
import argparse
import csv

VALID_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "road hole", "pit in road", "pit in the road"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "water logging", "inundated", "submerged", "knee-deep", "standing in water"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamppost", "light not working", "no light", "dark street", "lights out"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "debris", "litter", "dump", "scrap", "muck", "dead animal", "bins"],
    "Noise": ["noise", "loud", "noisy", "disturbance", "blaring", "honking", "construction noise", "dj ", "music"],
    "Road Damage": ["road damage", "broken road", "road crack", "road collapse", "road surface", "asphalt", "tarmac", "footpath", "tiles broken", "cracked"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "memorial", "heritage site", "heritage street"],
    "Heat Hazard": ["heat", "hot", "heatwave", "sunstroke", "dehydration", "extreme heat", "scorching"],
    "Drain Blockage": ["drain", "sewer", "clogged", "blocked drain", "overflow", "sewage", "storm drain", "gutter", "manhole", "drain blocked"],
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Find all matching categories
    matching_categories = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matching_categories.append(cat)
                break

    # Determine category
    category = "Other"
    if len(matching_categories) == 1:
        category = matching_categories[0]
    elif len(matching_categories) > 1:
        # Ambiguous - pick first match but flag for review
        category = matching_categories[0]

    # Determine priority
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # Build reason citing specific words from description
    matched_words = []
    if category in CATEGORY_KEYWORDS:
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in desc_lower:
                matched_words.append(kw)
    if not matched_words:
        # Fallback: use first few meaningful words from description
        words = desc_lower.split()
        matched_words = [w for w in words if len(w) > 3][:3]

    reason = f"Classification based on keywords: {', '.join(matched_words[:3])} found in description."

    # Flag ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif len(matching_categories) > 1:
        flag = "NEEDS_REVIEW"

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
        for i, row in enumerate(reader):
            try:
                complaint_id = row.get("complaint_id", "")
                description = row.get("description", "")
                if not complaint_id or not description:
                    print(f"Row {i+1}: missing complaint_id or description, skipping.")
                    continue
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                print(f"Row {i+1}: failed to classify — {e}")

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
