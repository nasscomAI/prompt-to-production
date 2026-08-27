"""
UC-0A — Complaint Classifier
Deterministic implementation guided by agents.md and skills.md.
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "waterlogged", "standing water", "inundated", "knee-deep"],
    "Streetlight": ["streetlight", "streetlights", "street light", "lights out", "light out", "lamp", "flickering", "sparking"],
    "Waste": ["garbage", "garbage bins", "waste", "trash", "overflowing", "dumped", "dead animal"],
    "Noise": ["noise", "music", "party", "loud", "midnight"],
    "Road Damage": ["cracked", "sinking", "road surface", "footpath", "tiles broken", "upturned", "surface"],
    "Heritage Damage": ["heritage", "historic", "monument", "old city", "heritage street"],
    "Heat Hazard": ["heat", "heatwave", "hot weather", "high temperature", "sun"],
    "Drain Blockage": ["drain", "drain blocked", "blocked", "clogged", "manhole", "sewer"],
}


def classify_complaint(row: dict) -> dict:
    """Classify one complaint row into the required schema."""
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description", "") or "").strip()
    desc_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description provided.",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = []
    matched_terms = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        found_terms = [kw for kw in keywords if kw in desc_lower]
        if found_terms:
            matched_categories.append(category)
            matched_terms.extend(found_terms)

    has_severity = any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"

    if len(matched_categories) == 1:
        category = matched_categories[0]
        evidence = matched_terms[0]
        reason = (
            f"The description contains '{evidence}', so the category is '{category}' and the priority is '{priority}' "
            f"because {'severity keywords were found' if has_severity else 'no severity keywords were found'}."
        )
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        evidence = ", ".join(f"'{term}'" for term in matched_terms[:3])
        reason = (
            f"The description contains {evidence}, so the category is ambiguous and marked '{category}' with priority '{priority}' "
            f"because {'severity keywords were found' if has_severity else 'no severity keywords were found'}."
        )
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        reason = (
            f"The description does not clearly match any allowed category, so the category is '{category}' and the priority is '{priority}' "
            f"because {'severity keywords were found' if has_severity else 'no severity keywords were found'}."
        )
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write a results CSV."""
    results = []
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append({**row, **classified})
            except Exception:
                complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
                results.append(
                    {
                        **(row if isinstance(row, dict) else {}),
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "System error during classification.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        fieldnames = list(results[0].keys()) if results else ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
