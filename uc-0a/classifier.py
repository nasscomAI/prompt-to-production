"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

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

URGENT_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_PATTERNS = [
    ("Pothole", ["pothole", "tyre damage", "tire damage", "wheel damage", "road depression"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drain blockage", "blocked sewer", "drainage blocked", "gutter blocked"]),
    ("Flooding", ["flood", "flooded", "water logging", "waterlogged", "knee-deep", "submerged", "inaccessible", "stranded"]),
    ("Streetlight", ["streetlight", "light out", "lights out", "dark at night", "flickering", "sparking", "lighting issue"]),
    ("Heritage Damage", ["heritage", "historical", "monument", "heritage street", "heritage area", "archaeological"]),
    ("Waste", ["garbage", "waste", "trash", "dumped", "dumping", "bins", "dead animal", "bulk waste", "fly tipping"]),
    ("Noise", ["noise", "loud", "music past midnight", "sound pollution", "honking", "late night music"]),
    ("Heat Hazard", ["heat", "scorching", "heatwave", "heat hazard", "dehydration", "sun stroke"]),
    ("Road Damage", ["cracked", "sinking", "broken pavement", "upturned", "road surface", "road damage", "depression", "footpath tiles broken"]),
]


def normalize_text(value: str) -> str:
    return " " + re.sub(r"\s+", " ", value.strip().lower()) + " "


def find_phrase(description: str, phrase: str) -> bool:
    return phrase in description


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    """
    description = (row.get("description") or "").strip()
    normalized = normalize_text(description)
    category = "Other"
    reason = "Unable to determine category from description."
    flag = ""

    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": category,
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    matches = []
    for name, keywords in CATEGORY_PATTERNS:
        for keyword in keywords:
            if find_phrase(normalized, normalize_text(keyword)):
                matches.append((name, keyword))
                break

    if len(matches) == 1:
        category, matched_keyword = matches[0]
        reason = "Description contains '{0}'.".format(matched_keyword)
    elif len(matches) > 1:
        category_counts = {}
        for name, keyword in matches:
            category_counts[name] = category_counts.get(name, 0) + 1

        chosen = max(category_counts.items(), key=lambda item: item[1])[0]
        category = chosen
        matched_keyword = next(k for n, k in matches if n == chosen)
        reason = "Description contains '{0}', best match is {1}.".format(matched_keyword, category)
        if len(set(category_counts)) > 1:
            flag = "NEEDS_REVIEW"
    else:
        reason = "No category keyword found in description."
        flag = "NEEDS_REVIEW"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        reason = "Matched category was not allowed; falling back to Other."
        flag = "NEEDS_REVIEW"

    lowered = normalized
    priority = "Urgent" if any(find_phrase(lowered, normalize_text(keyword)) for keyword in URGENT_KEYWORDS) else "Standard"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for row_index, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                except (KeyError, ValueError, TypeError) as error:
                    complaint_id = row.get("complaint_id", "")
                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Classification failed for row {0}: {1}".format(row_index, error),
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
