"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Water Supply",
    "Road Repair",
    "Street Light",
    "Sanitation",
    "Other",
]

URGENCY_KEYWORDS = {
    "injury",
    "injured",
    "child",
    "children",
    "kid",
    "kids",
}

CATEGORY_PATTERNS = [
    (
        "Water Supply",
        [
            r"\bwater\b",
            r"\bwater supply\b",
            r"\bno water\b",
            r"\bleak\b",
            r"\bpipe\b",
            r"\btap\b",
            r"\bdrinking water\b",
            r"\bwater leak\b",
        ],
    ),
    (
        "Road Repair",
        [
            r"\broad\b",
            r"\bpothole\b",
            r"\bcrack\b",
            r"\bbroken road\b",
            r"\broad repair\b",
            r"\bpavement\b",
            r"\bsinkhole\b",
        ],
    ),
    (
        "Street Light",
        [
            r"\bstreetlight\b",
            r"\bstreet light\b",
            r"\blamp post\b",
            r"\blight not working\b",
            r"\bdark street\b",
            r"\bno light\b",
            r"\bbroken light\b",
        ],
    ),
    (
        "Sanitation",
        [
            r"\bgarbage\b",
            r"\btrash\b",
            r"\bwaste\b",
            r"\bsewage\b",
            r"\bdrainage\b",
            r"\btoilet\b",
            r"\bcleaning\b",
            r"\bseptic\b",
        ],
    ),
]


def normalize_text(text: str) -> str:
    return text.strip().lower() if text is not None else ""


def _find_category_match(description: str) -> tuple[str, str]:
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return category, match.group(0)
    return "Other", ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id") or row.get("id") or row.get("ticket_id") or ""
    description = normalize_text(row.get("description") or row.get("complaint") or row.get("text") or "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing complaint description in the row.",
            "flag": "NEEDS_REVIEW",
        }

    category, excerpt = _find_category_match(description)
    priority = "Urgent" if any(keyword in description for keyword in URGENCY_KEYWORDS) else "Standard"
    flag = "" if category != "Other" else "NEEDS_REVIEW"

    if category == "Other":
        reason = f'No clear Water Supply, Road Repair, Street Light, or Sanitation keywords found in "{description[:60]}".'
    else:
        reason = f'Classified as {category} based on "{excerpt}" in the complaint description.'

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
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    rows = []

    with open(input_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row_number, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                if not result.get("complaint_id"):
                    result["complaint_id"] = str(row_number)
                rows.append(result)
            except Exception as exc:
                rows.append({
                    "complaint_id": row.get("complaint_id") or str(row_number),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Failed to classify row {row_number}: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
