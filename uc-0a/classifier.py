"""
UC-0A — Complaint Classifier
Implements the skills defined in skills.md under the enforcement rules in agents.md.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

SEVERITY_PATTERNS = [
    r"\binjur\w*", r"\bchild\w*", r"\bschool\w*", r"\bhospital\w*",
    r"\bambulance\w*", r"\bfire\w*", r"\bhazard\w*", r"\bfell\b", r"\bcollaps\w*",
]

CATEGORY_RULES = [
    ("Heritage Damage", [r"\bheritage\w*"]),
    ("Heat Hazard", [
        r"\bheat\w*", r"\bmelt(ing)?\b", r"\btemperat\w*", r"\bscorch\w*",
    ]),
    ("Flooding", [
        r"\bflood\w*", r"\brainwater\b", r"\bwater ?logg\w*", r"\binundat\w*",
    ]),
    ("Drain Blockage", [
        r"\bdrain\w*\s+(is\s+)?block\w*", r"\bblock\w*\s+drain\w*",
        r"\bclog\w*", r"\bchok\w*\s+drain\w*", r"\bdrain\w*\s+overflow\w*",
        r"\bdrain\w*",
    ]),
    ("Streetlight", [
        r"\bstreet[- ]?lights?\b", r"\blights?\s+out\b", r"\blamp\s?posts?\b",
        r"\bflicker\w*", r"\bunlit\b", r"\bdark(ness)?\b",
    ]),
    ("Noise", [
        r"\bnoise\w*", r"\bmusic\b", r"\bloud\w*", r"\bnoisy\b", r"\bdrill\w*",
        r"\bband\b", r"\bjackhammer\w*", r"\bidling\b", r"\bengines?\s+on\b",
    ]),
    ("Waste", [
        r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\blitter\w*",
        r"\bdump(ed|ing)?\b", r"\bdead\s+animal\b", r"\brefuse\b", r"\bsanitation\b",
    ]),
    ("Pothole", [r"\bpotholes?\b", r"\bpot\s?holes?\b"]),
    ("Road Damage", [
        r"\broad\s+surface\b", r"\bcrack\w*", r"\bsink(ing)?\b", r"\bsubsid\w*",
        r"\bfootpath\b", r"\bupturn\w*", r"\bmanhole\b", r"\bcollapse\w*",
        r"\bcrater\w*",
    ]),
]


def _find_matches(text, patterns):
    found, seen = [], set()
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m and m.group(0).lower() not in seen:
            seen.add(m.group(0).lower())
            found.append(m.group(0))
    return found


def _quote_words(words):
    return ", ".join('"%s"' % w for w in words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Uses only complaint_id and description, per agents.md context exclusions.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty; classification not possible.",
            "flag": "NEEDS_REVIEW",
        }

    category, cited = None, []
    for candidate, patterns in CATEGORY_RULES:
        hits = _find_matches(description, patterns)
        if hits:
            if category is None:
                category = candidate
            cited.extend(hits)

    if category is None or category not in CATEGORIES:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No allowed taxonomy category could be determined from the description.",
            "flag": "NEEDS_REVIEW",
        }

    severity_hits = _find_matches(description, SEVERITY_PATTERNS)
    priority = "Urgent" if severity_hits else "Standard"

    reason = 'Category %s based on %s in the description' % (
        category, _quote_words(cited[:3]),
    )
    if severity_hits:
        reason += '; priority Urgent due to %s' % _quote_words(severity_hits[:2])
    reason += "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags null/bad rows instead of crashing; always produces a complete output file.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            results.append({
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": "Classification failed; manual review required.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
