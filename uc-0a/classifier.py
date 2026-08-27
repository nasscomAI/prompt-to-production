"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("pothole", "Pothole"),
    ("flood", "Flooding"),
    ("waterlogging", "Flooding"),
    ("water-logged", "Flooding"),
    ("heritage", "Heritage Damage"),
    ("historic", "Heritage Damage"),
    ("streetlight", "Streetlight"),
    ("lights out", "Streetlight"),
    ("light out", "Streetlight"),
    ("flickering", "Streetlight"),
    ("drain", "Drain Blockage"),
    ("drainage", "Drain Blockage"),
    ("garbage", "Waste"),
    ("waste", "Waste"),
    ("bin", "Waste"),
    ("dead animal", "Waste"),
    ("dumping", "Waste"),
    ("overflowing", "Waste"),
    ("music", "Noise"),
    ("noise", "Noise"),
    ("loud", "Noise"),
    ("drilling", "Noise"),
    ("road surface", "Road Damage"),
    ("cracked", "Road Damage"),
    ("sinking", "Road Damage"),
    ("subsided", "Road Damage"),
    ("collapsed", "Road Damage"),
    ("footpath", "Road Damage"),
    ("paving", "Road Damage"),
    ("manhole", "Road Damage"),
    ("heat", "Heat Hazard"),
]


def _check_priority(desc_lower: str) -> str:
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _find_category(desc_lower: str) -> str | None:
    for keyword, category in CATEGORY_RULES:
        if keyword in desc_lower:
            return category
    return None


def _build_reason(desc: str, category: str, priority: str) -> str:
    desc_lower = desc.lower()
    matched_keywords = []
    for kw, _ in CATEGORY_RULES:
        if kw in desc_lower and kw not in matched_keywords:
            matched_keywords.append(kw)
    if priority == "Urgent":
        severity_kws = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
        if severity_kws:
            parts = []
            if matched_keywords:
                parts.append(
                    f"mentions '{', '.join(matched_keywords[:3])}'"
                )
            parts.append(f"contains severity keyword '{severity_kws[0]}'")
            return (
                f"Description {'; '.join(parts)}; "
                f"classified as {category} with {priority} priority."
            )
    if matched_keywords:
        return (
            f"Description mentions '{', '.join(matched_keywords[:3])}', "
            f"classified as {category}."
        )
    return f"Description does not clearly map to a category, classified as {category}."


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    priority = _check_priority(desc_lower)
    category = _find_category(desc_lower)

    if category is None:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "Description does not clearly map to any category",
            "flag": "NEEDS_REVIEW",
        }

    reason = _build_reason(description, category, priority)
    flag = ""
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input file: {e}")
        exit(1)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", "unknown"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Error processing row: {e}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")
        exit(1)

    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
