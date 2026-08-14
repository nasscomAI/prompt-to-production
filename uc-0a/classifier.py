"""
UC-0A — Complaint Classifier
Reads a citizen complaint CSV and assigns category, priority, reason, and flag
per the enforcement rules in agents.md and skills.md.
"""
import argparse
import csv
import re

CATEGORIES = [
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

URGENT_KEYWORDS = [
    r"\binjury\b",
    r"\bchild\b",
    r"\bschool\b",
    r"\bhospital\b",
    r"\bambulance\b",
    r"\bfire\b",
    r"\bhazard\b",
    r"\bfell\b",
    r"\bcollapse\b",
]

CATEGORY_RULES = [
    (
        "Pothole",
        [r"\bpothole\b", r"\bpot[\s-]?holes?\b", r"\bcrater\b"],
    ),
    (
        "Flooding",
        [r"\bflood", r"\bwaterlogged\b", r"\bstanding water\b", r"\bsubmerged\b"],
    ),
    (
        "Streetlight",
        [r"\bstreetlights?\b", r"\bstreet light\b", r"\blights? out\b", r"\bflicker", r"\bspark", r"\blamp\b"],
    ),
    (
        "Waste",
        [r"\bgarbage\b", r"\btrash\b", r"\blitter\b", r"\brubbish\b", r"\bwaste\b", r"\bdead animal\b", r"\bbins?\b", r"\brefuse\b", r"\bdebris\b"],
    ),
    (
        "Noise",
        [r"\bnoise\b", r"\bloud music\b", r"\bwedding\b", r"\bhonking\b", r"\bparty\b", r"\bamplif"],
    ),
    (
        "Road Damage",
        [r"\broad surface\b", r"\bcracked\b", r"\bsinking\b", r"\bfootpath\b", r"\bmanhole cover\b", r"\brugs\b", r"\brough road\b"],
    ),
    (
        "Heritage Damage",
        [r"\bheritage\b", r"\bmonument\b", r"\bhistoric\b"],
    ),
    (
        "Heat Hazard",
        [r"\bheat\b", r"\bheatwave\b", r"\bheat wave\b", r"\bscorching\b"],
    ),
    (
        "Drain Blockage",
        [r"\bdrain\b", r"\bdrainage\b", r"\bclogged\b", r"\bchoked\b", r"\bsilted\b", r"\boverflowing drain\b"],
    ),
]


def _contains(text: str, patterns) -> bool:
    return any(re.search(p, text) for p in patterns)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    lowered = description.lower()

    matches = [
        category
        for category, patterns in CATEGORY_RULES
        if _contains(lowered, patterns)
    ]

    if not description:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description is missing or empty, so no category can be determined."
    elif not matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f'No category keyword found in: "{description}".'
    elif len(matches) > 1:
        category = matches[0]
        flag = "NEEDS_REVIEW"
        reason = (
            f'Description matches multiple categories ({", ".join(matches)}): "{description}".'
        )
    else:
        category = matches[0]
        flag = ""
        reason = (
            f'Category matched keyword "{category}" in description: "{description}".'
        )

    priority = "Urgent" if _contains(lowered, URGENT_KEYWORDS) else "Standard"

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
    Preserves the original row count and never drops or invents rows.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            result = classify_complaint(row)
            output_row = dict(row)
            output_row["category"] = result["category"]
            output_row["priority"] = result["priority"]
            output_row["reason"] = result["reason"]
            output_row["flag"] = result["flag"]
            writer.writerow(output_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
