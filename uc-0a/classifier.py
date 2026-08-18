"""
UC-0A Complaint Classifier
Classifies citizen complaints by category, priority, and reason.
Enforces the exact schema from uc-0a/README.md to avoid taxonomy drift,
severity blindness, and hallucinated sub-categories.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "waterlog"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "light out", "flickering"]),
    ("Waste", ["garbage", "waste", "dead animal", "dumped", "bins"]),
    ("Noise", ["music", "noise", "loud"]),
    ("Road Damage", ["road surface", "footpath", "cracked", "sinking"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat wave", "sunstroke", "extreme heat"]),
    ("Drain Blockage", ["drain blocked", "drain block", "clogged drain"]),
]


def classify_complaint(description: str) -> dict:
    """One complaint description in -> category + priority + reason + flag out."""
    text = description.lower()

    matched_categories = []
    matched_terms = []
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in text:
                matched_categories.append(category)
                matched_terms.append(kw)
                break

    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in text]

    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"No listed category keywords found in: '{description.strip()}'."
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = f"Classified as {category} due to '{matched_terms[0]}' in description."
    else:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        terms = "', '".join(matched_terms)
        reason = (
            f"Ambiguous between {', '.join(matched_categories)} "
            f"(matched terms: '{terms}') - defaulted to {category}, flagged for human review."
        )

    if severity_hits:
        priority = "Urgent"
        reason += f" Marked Urgent due to severity keyword(s): {', '.join(severity_hits)}."
    else:
        priority = "Standard"

    assert category in ALLOWED_CATEGORIES, f"Category '{category}' not in allowed list"

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str) -> None:
    """Reads input CSV, applies classify_complaint per row, writes output CSV."""
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

    for row in rows:
        result = classify_complaint(row.get("description", ""))
        row.update(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Classified {len(rows)} rows -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
