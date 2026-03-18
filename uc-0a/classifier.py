"""
UC-0A — Complaint Classifier
Rule-based classifier enforcing the RICE rules defined in agents.md and skills.md.
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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("Pothole",         r"\bpotholes?\b"),
    ("Flooding",        r"\bfloo(?:d|ds|ded|ding)\b"),
    ("Streetlight",     r"\bstreetlights?\b|\bstreet lights?\b|\blights? out\b|\blights? flickering\b|\blights? sparking\b"),
    ("Waste",           r"\bgarbage\b|\bwaste\b|\bdumped\b|\bdump\b|\bbins?\b|\bdead animal\b"),
    ("Noise",           r"\bnoise\b|\bmusic\b|\bsound\b|\bloud\b"),
    ("Road Damage",     r"\bcracked\b|\bsinking\b|\broad surface\b|\bmanhole\b|\bfootpath\b|\btiles?\b|\broad damage\b|\bupturned\b"),
    ("Heritage Damage", r"\bheritage\b"),
    ("Heat Hazard",     r"\bheat\b|\btemperature\b"),
    ("Drain Blockage",  r"\bdrain\b|\bblocked\b|\bblockage\b|\bblocking\b"),
]


def _detect_category(description: str) -> tuple:
    """Return (category, is_ambiguous) based on keyword matching."""
    lower = description.lower()
    matched = []
    for cat, pattern in CATEGORY_RULES:
        if re.search(pattern, lower):
            matched.append(cat)

    if len(matched) == 1:
        return matched[0], False
    elif len(matched) > 1:
        # Multiple matches — pick the most specific / first, but flag for review
        return matched[0], True
    else:
        return "Other", True


def _detect_priority(description: str) -> str:
    """Return Urgent if any severity keyword is present, else Standard."""
    lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower):
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """Return a one-sentence reason citing specific words from the description."""
    lower = description.lower()

    # Quote the first 10 words of the description as the key evidence
    words = description.split()
    snippet = " ".join(words[:10]) if len(words) > 10 else description

    if priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower):
                return (
                    f"Classified as {category} with Urgent priority because description "
                    f"contains the severity keyword '{kw}': \"{snippet}\"."
                )

    return (
        f"Classified as {category} based on description keywords: \"{snippet}\"."
    )


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

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
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    skipped = 0

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as exc:
                print(f"Warning: skipping row {i} due to error: {exc}")
                skipped += 1

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    needs_review = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Processed {len(results)} rows. "
          f"NEEDS_REVIEW: {needs_review}. Skipped: {skipped}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
