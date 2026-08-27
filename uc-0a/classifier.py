"""
UC-0A — Complaint Classifier

Implements the contracts defined in agents.md and skills.md:
  - Fixed 10-value taxonomy, no invented categories.
  - Severity keywords force Urgent and are never downgraded.
  - reason must quote a literal substring (>=3 chars) from the description.
  - Ambiguous or short input -> category=Other, flag=NEEDS_REVIEW.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords from README.md / agents.md enforcement rule 2.
# Whole-word, case-insensitive. Order does not matter.
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category -> ordered keyword list. First match wins; Pothole is checked
# before Road Damage so a "pothole on damaged road" stays a Pothole.
CATEGORY_KEYWORDS = [
    ("Pothole",         ["pothole"]),
    ("Flooding",        ["flood", "waterlog", "water-log", "inundat", "submerg"]),
    ("Drain Blockage",  ["drain", "sewer", "manhole", "gutter", "blocked drainage"]),
    ("Streetlight",     ["streetlight", "street light", "lamppost", "lamp post",
                         "no light", "dark street"]),
    ("Waste",           ["garbage", "trash", "litter", "dustbin", "refuse heap",
                         "dump", "waste pile", "uncollected waste"]),
    ("Noise",           ["noise", "loud music", "honking", "dj", "loudspeaker", "blaring"]),
    ("Heritage Damage", ["heritage", "monument", "fort wall", "historic", "statue", "memorial"]),
    ("Heat Hazard",     ["heatwave", "heat wave", "scorching", "no shade", "melting tar"]),
    ("Road Damage",     ["road damage", "cracked road", "broken road", "road broken",
                         "asphalt", "road surface", "crater"]),
]

# Triggers a Low priority (purely cosmetic / informational).
LOW_PRIORITY_KEYWORDS = ["cosmetic", "minor", "for record", "informational", "low priority"]

MIN_DESCRIPTION_LEN = 5


def _find_severity_quote(description: str) -> str | None:
    """Return the first severity keyword that appears as a whole word, else None."""
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", description, flags=re.IGNORECASE):
            return kw
    return None


def _match_category(description: str) -> tuple[str, str | None]:
    """Return (category, matched_phrase) or ("Other", None) if no match."""
    lowered = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in lowered:
                return category, kw
    return "Other", None


def _quote_from(description: str, phrase: str | None) -> str:
    """Return a substring of description that contains phrase verbatim, or
    the first ~80 chars of description as a fallback."""
    if phrase:
        idx = description.lower().find(phrase.lower())
        if idx >= 0:
            return description[idx : idx + len(phrase)]
    return description.strip()[:80]


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row. See skills.md > classify_complaint."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if len(description) < MIN_DESCRIPTION_LEN:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "description missing or too short to classify",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_phrase = _match_category(description)
    severity_word = _find_severity_quote(description)

    if severity_word:
        priority = "Urgent"
        quote = severity_word
    elif any(low_kw in description.lower() for low_kw in LOW_PRIORITY_KEYWORDS):
        priority = "Low"
        quote = matched_phrase
    else:
        priority = "Standard"
        quote = matched_phrase

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    quoted = _quote_from(description, quote)
    if category == "Other" and severity_word:
        reason = f'severity term "{quoted}" present but category unclear from description'
    elif category == "Other":
        reason = f'no taxonomy match in description: "{quoted}"'
    else:
        reason = f'description mentions "{quoted}"'

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write results CSV. See skills.md."""
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    total = needs_review = errors = 0

    with open(input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=output_fields)
        writer.writeheader()

        for row in rows:
            total += 1
            cid = (row.get("complaint_id") or "").strip()
            if not cid:
                errors += 1
                print(f"skip: row {total} missing complaint_id", file=sys.stderr)
                continue
            try:
                result = classify_complaint(row)
            except Exception as exc:
                errors += 1
                result = {
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"classifier error: {type(exc).__name__}",
                    "flag": "NEEDS_REVIEW",
                }
            if result["flag"] == "NEEDS_REVIEW":
                needs_review += 1
            writer.writerow(result)

    print(f"rows={total} needs_review={needs_review} errors={errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
