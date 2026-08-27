"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
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

CATEGORY_KEYWORDS = [
    ("Heritage Damage", ["heritage"]),
    ("Streetlight", ["streetlight", "lights out", "light out", "street lights", "street light", "flickering", "sparking", "dark at night"]),
    ("Heat Hazard", ["heat hazard", "heatwave", "heat stress", "high temperature", "heat"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "blocked drain", "drains blocked", "drain is blocked", "blocked gutter", "gutter blocked"]),
    ("Flooding", ["flooded", "flooding", "flood", "waterlogged", "knee-deep", "inaccessible"]),
    ("Pothole", ["pothole", "potholes", "tyre damage"]),
    ("Waste", ["garbage", "trash", "waste", "bins", "dumped", "dumping", "dead animal", "overflowing bins", "smell affecting shoppers"]),
    ("Noise", ["noise", "music past midnight", "loud music", "playing music", "speaker", "sound past midnight"]),
    ("Road Damage", ["road surface cracked", "road surface", "cracked", "sinking", "depression", "tiles broken", "broken", "manhole cover missing", "footpath tiles"]),
]

OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]


def quote_phrase(phrase: str) -> str:
    if "'" not in phrase:
        return f"'{phrase}'"
    if '"' not in phrase:
        return f'"{phrase}"'
    safe_phrase = phrase.replace("'", "")
    return f"'{safe_phrase}'"


def detect_severity(text: str) -> bool:
    return any(keyword in text for keyword in SEVERITY_KEYWORDS)


def find_category_matches(text: str) -> list:
    matches = []
    for category, terms in CATEGORY_KEYWORDS:
        for term in terms:
            if term in text:
                matches.append((category, term))
                break
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    normalized = description.lower()

    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    severity = "Urgent" if detect_severity(normalized) else "Standard"
    category_matches = find_category_matches(normalized)
    categories = [category for category, _ in category_matches]
    unique_categories = list(dict.fromkeys(categories))

    if not unique_categories:
        citation = description.split(".")[0].strip()
        if not citation:
            citation = description
        return {
            "category": "Other",
            "priority": severity,
            "reason": f"Description mentions {quote_phrase(citation)} which does not match any defined category.",
            "flag": "NEEDS_REVIEW",
        }

    chosen_category = unique_categories[0]
    flag = ""
    if len(unique_categories) > 1:
        flag = "NEEDS_REVIEW"

    cited_term = category_matches[0][1]
    if chosen_category == "Other":
        cited_term = description.split(".")[0].strip()

    reason = f"Complaint mentions {quote_phrase(cited_term)} and is classified as {chosen_category}."
    return {
        "category": chosen_category,
        "priority": severity,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        results = []

        for row in reader:
            try:
                result = classify_complaint(row)
                if not isinstance(result, dict):
                    raise ValueError("classify_complaint must return a dict")
                output_row = {field: str(result.get(field, "")).strip() for field in OUTPUT_FIELDS}
            except Exception as exc:
                output_row = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(output_row)

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
