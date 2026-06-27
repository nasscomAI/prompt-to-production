"""
UC-0A — Complaint Classifier
Builds on the agent/skill definitions in agents.md and skills.md.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other",
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("Pothole",        [r"\bpotholes?\b", r"\bpot[\s-]?holes?\b"]),
    ("Flooding",       [r"\bflood(?:ed|ing|s)?\b", r"\bwaterlogged\b",
                        r"\bstanding water\b", r"\bknee[\s-]?deep\b",
                        r"\binaccessible\b"]),
    ("Streetlight",    [r"\bstreetlights?\b", r"\blight(?:s)?\s+out\b",
                        r"\bflickering\b", r"\bsparking\b",
                        r"\blamp\b", r"\bunlit\b",
                        r"\bdark(?:ness)?\b"]),
    ("Waste",          [r"\bgarbage\b", r"\bwaste\b", r"\bbin(?:s)?\b",
                        r"\bdump(?:ed)?\b", r"\btrash\b", r"\blitter\b",
                        r"\bdead animal\b", r"\boverflowing\b"]),
    ("Noise",          [r"\bnoise\b", r"\bloud\b", r"\bmusic\b",
                        r"\bnoisy\b", r"\bband\b", r"\bplaying\b",
                        r"\bamplifiers?\b"]),
    ("Road Damage",    [r"\broad surface\b", r"\bcracked\b",
                        r"\bsinking\b", r"\bfootpath\b",
                        r"\bpavement\b", r"\broad damage\b"]),
    ("Heritage Damage", [r"\bheritage\b"]),
    ("Heat Hazard",    [r"\bheat\b", r"\bheatwave\b", r"\bheat wave\b",
                        r"\btemperature", r"\b°c\b", r"\bdegrees?\b",
                        r"\bunbearable\b"]),
    ("Drain Blockage", [r"\bdrain(?:s|ing|ed|age)?\b", r"\bsewer\b",
                        r"\bmanhole\b", r"\bblocked\b"]),
]


def _matches_category(description: str, patterns: list) -> bool:
    return any(re.search(p, description, re.IGNORECASE) for p in patterns)


def _check_urgent(description: str) -> bool:
    return any(
        re.search(r"\b" + re.escape(kw) + r"\b", description, re.IGNORECASE)
        for kw in SEVERITY_KEYWORDS
    )


def _assign_category(description: str) -> tuple:
    """
    Returns (category, flag).
    flag is 'NEEDS_REVIEW' when ambiguous, empty string otherwise.
    """
    if not description or not description.strip():
        return "Other", "NEEDS_REVIEW"

    matches = []
    for cat, patterns in CATEGORY_RULES:
        if _matches_category(description, patterns):
            matches.append(cat)

    if len(matches) == 0:
        return "Other", ""
    if len(matches) == 1:
        return matches[0], ""
    if len(matches) > 1:
        return matches[0], "NEEDS_REVIEW"


def _build_reason(description: str, category: str) -> str:
    desc_lower = description.lower()
    for cat, patterns in CATEGORY_RULES:
        if cat != category:
            continue
        for p in patterns:
            m = re.search(p, description, re.IGNORECASE)
            if m:
                excerpt = description[max(0, m.start()-5):m.end()+20].strip()
                return (
                    f"The description '{excerpt}...' contains "
                    f"'{m.group()}', matching category '{cat}'."
                )
    return f"The description '{description[:60]}...' did not match any category keyword clearly."


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    category, flag = _assign_category(description)
    priority = "Urgent" if _check_urgent(description) else "Standard"
    reason = _build_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Empty or invalid CSV: {input_path}")

        required_cols = {"complaint_id", "description"}
        missing = required_cols - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}"
            )

        results = []
        for i, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)
            except Exception as e:
                print(
                    f"Warning: row {i} failed ({e}). Skipping.",
                    file=sys.stderr,
                )
                continue
            results.append(result)

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
