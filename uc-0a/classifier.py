"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORY_OPTIONS = [
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

CATEGORY_PATTERNS = [
    ("Heritage Damage", ["heritage", "old city", "heritage street"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drainage blocked", "drainage"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "dark at night", "flicker", "flickering", "sparking"]),
    ("Waste", ["garbage", "waste", "trash", "dumped", "dumping", "bins", "bulk waste", "refuse", "dead animal"]),
    ("Noise", ["music", "noise", "loud", "speaker", "midnight", "late night"]),
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "flooded", "waterlogged", "knee-deep", "standing water", "inundated", "bridge approach floods"]),
    ("Road Damage", ["road surface cracked", "sinking", "upturned", "broken tiles", "manhole cover missing", "footpath tiles", "pavement", "road damage", "surface cracked"]),
    ("Heat Hazard", ["heat", "high temperature", "heat hazard"]),
]


def _normalize_text(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _find_matches(text: str, patterns: list[str]) -> list[str]:
    matches = []
    for pattern in patterns:
        if pattern in text:
            matches.append(pattern)
    return matches


def _select_category(description: str) -> tuple[str, list[str]]:
    normalized = _normalize_text(description)
    for category, patterns in CATEGORY_PATTERNS:
        matches = _find_matches(normalized, patterns)
        if matches:
            return category, matches
    return "Other", []


def _select_priority(description: str) -> tuple[str, list[str]]:
    normalized = _normalize_text(description)
    severity_matches = _find_matches(normalized, SEVERITY_KEYWORDS)
    if severity_matches:
        return "Urgent", severity_matches
    return "Standard", []


def _build_reason(description: str, category: str, category_matches: list[str], severity_matches: list[str]) -> str:
    cited = []
    if category_matches:
        cited.extend(category_matches)
    if severity_matches:
        cited.extend(severity_matches)

    if cited:
        unique_cited = []
        for term in cited:
            if term not in unique_cited:
                unique_cited.append(term)
        quoted = ", ".join(f"'{term}'" for term in unique_cited[:3])
        return f"Mentions {quoted}."

    if description:
        first_phrase = " ".join(description.split()[:8])
        return f"Description indicates issue: {first_phrase}."

    return "No description available."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip() or "UNKNOWN"
    description = _normalize_text(row.get("description", ""))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty description.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_matches = _select_category(description)
    priority, severity_matches = _select_priority(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    reason = _build_reason(description, category, category_matches, severity_matches)

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
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row_index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                complaint_id = str(row.get("complaint_id", "")).strip() or f"row-{row_index}"
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Failed to classify row: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow({field: result.get(field, "") for field in output_fields})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
