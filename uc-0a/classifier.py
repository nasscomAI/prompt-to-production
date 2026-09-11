"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole in road", "road hole"],
    "Flooding": ["flood", "waterlogged", "water logging", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp post", "no light"],
    "Waste": ["garbage", "waste", "trash", "litter", "dump"],
    "Noise": ["noise", "loud", "sound pollution"],
    "Road Damage": ["road damage", "cracked road", "broken road", "damaged road"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "sunstroke", "extreme temperature"],
    "Drain Blockage": ["drain", "sewage", "blocked drain", "clogged"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was empty or missing, so no category could be determined.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- category matching ---
    matched_categories = []
    matched_words = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                matched_words.append(kw)
                break

    matched_categories = list(dict.fromkeys(matched_categories))  # dedupe, keep order

    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No description keywords matched any defined category."
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = f"Description mentions '{matched_words[0]}', matching category {category}."
    else:
        # genuinely ambiguous between two+ categories
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason = (
            f"Description mentions both '{matched_words[0]}' and '{matched_words[1]}', "
            f"making the category ambiguous between {matched_categories[0]} and {matched_categories[1]}."
        )

    # --- priority ---
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_severity:
        priority = "Urgent"
        reason += f" Marked Urgent due to severity keyword(s): {', '.join(found_severity)}."
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, always produces output.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_fields = list(fieldnames)
    for extra in ["category", "priority", "reason", "flag"]:
        if extra not in output_fields:
            output_fields.append(extra)

    results = []
    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception as e:
            classification = {
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row failed to classify due to an error: {e}",
                "flag": "NEEDS_REVIEW",
            }
        merged = dict(row)
        merged["category"] = classification["category"]
        merged["priority"] = classification["priority"]
        merged["reason"] = classification["reason"]
        merged["flag"] = classification["flag"]
        results.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")