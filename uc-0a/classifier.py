"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path

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

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

CATEGORY_KEYWORDS = {
    "Pothole": ("pothole",),
    "Flooding": ("flood", "flooded", "waterlogged", "water logging", "waterlogging", "stranded"),
    "Streetlight": ("streetlight", "street light", "lights out", "flickering", "sparking", "dark at night"),
    "Waste": ("garbage", "waste", "bins", "dumped", "dead animal", "trash", "smell", "overflowing"),
    "Noise": ("noise", "loud", "music", "midnight"),
    "Road Damage": ("road surface", "cracked", "sinking", "broken", "upturned", "tiles broken", "manhole cover missing"),
    "Heritage Damage": ("heritage", "historic", "old city"),
    "Heat Hazard": ("heat", "heatwave", "hot", "sunstroke", "dehydration"),
    "Drain Blockage": ("drain blocked", "drainage", "blocked drain", "choked drain", "sewer blocked", "manhole"),
}


def _build_text(row: dict) -> str:
    return " ".join(str(value) for value in row.values() if value is not None).strip()


def _extract_matches(text: str, candidates: tuple[str, ...]) -> list[str]:
    return [token for token in candidates if token in text]


def _single_sentence(message: str) -> str:
    cleaned = " ".join(message.strip().split())
    return cleaned if cleaned.endswith(".") else f"{cleaned}."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    full_text = _build_text(row)
    lowered_text = full_text.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": _single_sentence("Insufficient complaint text for classification"),
            "flag": "NEEDS_REVIEW",
        }

    category_hits: dict[str, list[str]] = {}
    for category, tokens in CATEGORY_KEYWORDS.items():
        matches = _extract_matches(lowered_text, tokens)
        if matches:
            category_hits[category] = matches

    category = "Other"
    category_match_tokens: list[str] = []
    flag = ""

    if category_hits:
        ranked = sorted(category_hits.items(), key=lambda item: len(item[1]), reverse=True)
        top_score = len(ranked[0][1])
        top_categories = [item for item in ranked if len(item[1]) == top_score]

        if len(top_categories) == 1:
            category = top_categories[0][0]
            category_match_tokens = top_categories[0][1]
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            category_match_tokens = sorted({token for _, tokens in top_categories for token in tokens})
    else:
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if any(token in lowered_text for token in SEVERITY_KEYWORDS) else "Standard"

    if category == "Other" and not category_match_tokens:
        reason = _single_sentence("Category is ambiguous from complaint wording and requires manual review")
        flag = "NEEDS_REVIEW"
    elif category == "Other":
        reason = _single_sentence(
            f"Matched multiple category cues ({', '.join(category_match_tokens)}), so manual review is required"
        )
        flag = "NEEDS_REVIEW"
    else:
        reason = _single_sentence(
            f"Classified as {category} based on complaint words: {', '.join(category_match_tokens)}"
        )

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
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_rows: list[dict] = []
    with input_file.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV is missing header row")
        if "description" not in reader.fieldnames:
            raise ValueError("Input CSV must include a 'description' column")

        for raw_row in reader:
            try:
                output_rows.append(classify_complaint(raw_row))
            except Exception as exc:
                output_rows.append(
                    {
                        "complaint_id": str(raw_row.get("complaint_id", "")).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": _single_sentence(f"Row processing error: {exc}"),
                        "flag": "NEEDS_REVIEW",
                    }
                )

    output_headers = ["complaint_id", "category", "priority", "reason", "flag"]
    with Path(output_path).open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_headers)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
