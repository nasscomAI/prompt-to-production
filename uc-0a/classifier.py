"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    lower = description.lower()

    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance",
        "fire", "hazard", "fell", "collapse"
    ]
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooding", "flooded"],
        "Streetlight": ["streetlight", "street light", "light out", "light not working"],
        "Waste": ["garbage", "trash", "waste", "litter", "dumping", "dump"] ,
        "Noise": ["noise", "loud", "sound", "honking", "honk", "music"],
        "Road Damage": ["road damage", "pavement", "asphalt", "crack", "cracks", "uneven", "sinkhole"],
        "Heritage Damage": ["heritage", "monument", "statue", "temple", "historic", "heritage site", "protected"],
        "Heat Hazard": ["heat", "hot", "heat hazard", "extreme heat", "heatwave", "burn"],
        "Drain Blockage": ["drain", "blocked", "clogged", "sewer", "gutter", "spout", "drainage"],
    }

    matched_categories = []
    matched_keywords = {}
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in lower:
                matched_categories.append(category)
                matched_keywords[category] = keyword
                break

    severity_matches = [keyword for keyword in severity_keywords if keyword in lower]

    if not description:
        category = "Other"
        reason = "Description is missing, so the complaint is marked as Other and flagged for review."
        priority = "Standard"
        flag = "NEEDS_REVIEW"
    else:
        if len(matched_categories) == 1:
            category = matched_categories[0]
        elif len(matched_categories) > 1:
            category = "Other"
        else:
            category = "Other"

        urgent = bool(severity_matches)
        priority = "Urgent" if urgent else "Standard"

        if category == "Other":
            if matched_categories:
                reason = (
                    "Description matches multiple categories (" + ", ".join(matched_categories) + ") "
                    "and is therefore set to Other with review."
                )
                flag = "NEEDS_REVIEW"
            else:
                reason = "No exact UC-0A category keywords were found in the description."
                flag = "NEEDS_REVIEW"
        else:
            matched_keyword = matched_keywords.get(category, category)
            reason = (
                f"Classified as {category} because the description mentions '{matched_keyword}'."
            )
            flag = ""

        if urgent and flag != "NEEDS_REVIEW":
            keyword_str = ", ".join(severity_matches)
            reason = (
                f"Classified as {category} with Urgent priority because the description mentions "
                f"severity keyword(s): {keyword_str}."
            )

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        if not rows:
            fieldnames = reader.fieldnames or []
        else:
            fieldnames = rows[0].keys()

    output_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for index, row in enumerate(rows, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Failed to classify row {index}: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            output_row = {**row}
            output_row.update(result)
            writer.writerow(output_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
