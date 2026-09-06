"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


ALLOWED_CATEGORIES = frozenset({
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
})

SEVERITY_KEYWORDS = frozenset({
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
})

# Rules are ordered so that a direct complaint type wins over contextual words.
CATEGORY_KEYWORDS = (
    ("Pothole", ("pothole", "potholes")),
    ("Flooding", ("flooded", "floods", "knee-deep", "rainwater")),
    ("Streetlight", ("streetlight", "streetlights", "lights out", "unlit", "darkness")),
    ("Waste", ("waste", "garbage", "rubbish", "trash", "dead animal")),
    ("Noise", ("noise", "music", "wedding band", "drilling", "amplifier", "engines on")),
    ("Heat Hazard", ("heat", "heatwave", "temperature", "temperatures", "melting", "full sun")),
    ("Drain Blockage", ("drain blocked", "drain completely blocked", "stormwater drain", "draining directly")),
    ("Road Damage", ("road collapsed", "road subsidence", "road subsided", "road surface cracked", "road surface buckled", "footpath broken", "footpath tiles broken", "paving")),
    ("Heritage Damage", ("heritage", "historic", "ancient")),
)

OUTPUT_FIELDS = ("complaint_id", "category", "priority", "reason", "flag")


def _first_matching_keyword(text: str, keywords: tuple[str, ...] | frozenset[str]):
    """Return the first keyword and its exact text from the description."""
    for keyword in keywords:
        start = text.find(keyword)
        if start != -1:
            return text[start:start + len(keyword)]
    return None


def _description_excerpt(description: str) -> str:
    """Return a short, verbatim phrase suitable for a one-sentence reason."""
    first_clause = description.split(".", 1)[0].strip()
    return first_clause or description[:80].strip()


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Uses only the complaint description as evidence.
    """
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    raw_description = row.get("description") if isinstance(row, dict) else None
    description = raw_description.strip() if isinstance(raw_description, str) else ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classification unavailable because the description is missing",
            "flag": "NEEDS_REVIEW",
        }

    lowered_description = description.lower()
    category = "Other"
    category_evidence = None

    for candidate, keywords in CATEGORY_KEYWORDS:
        evidence = _first_matching_keyword(lowered_description, keywords)
        if evidence is not None:
            category = candidate
            start = lowered_description.find(evidence)
            category_evidence = description[start:start + len(evidence)]
            break

    severity_evidence = _first_matching_keyword(
        lowered_description, tuple(sorted(SEVERITY_KEYWORDS))
    )
    priority = "Urgent" if severity_evidence is not None else "Standard"

    if severity_evidence is not None:
        start = lowered_description.find(severity_evidence)
        severity_evidence = description[start:start + len(severity_evidence)]

    if category == "Other":
        excerpt = _description_excerpt(description)
        if severity_evidence is not None:
            reason = (
                f'Category needs review because "{excerpt}" does not identify an approved '
                f'complaint type, while "{severity_evidence}" triggers Urgent priority.'
            )
        else:
            reason = (
                f'Category needs review because "{excerpt}" does not identify an '
                "approved complaint type."
            )
        flag = "NEEDS_REVIEW"
    elif severity_evidence is not None and severity_evidence.lower() != category_evidence.lower():
        reason = (
            f'Classified as {category} with Urgent priority because the description '
            f'contains "{category_evidence}" and "{severity_evidence}".'
        )
        flag = ""
    else:
        reason = (
            f'Classified as {category} because the description contains '
            f'"{category_evidence}".'
        )
        flag = ""

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

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
    
    A failed row is written as Other/NEEDS_REVIEW without stopping the batch.
    """
    with open(input_path, "r", encoding="utf-8-sig", newline="") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None or "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a description column")

        with open(output_path, "w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Classification unavailable because the row could not be processed.",
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
