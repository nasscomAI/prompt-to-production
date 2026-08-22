"""
UC-0A — Complaint Classifier
Built from the RICE prompt in agents.md, following the enforcement rules
there. Deterministic keyword-rule engine (not a free-form LLM call) so the
enforcement rules are directly testable and reproducible — this is the fix
for taxonomy drift and false confidence described in agents.md.
"""
import argparse
import csv
import re

# Category detection: (category_name, compiled keyword regex). Order matters
# only for tie-breaking when a description matches more than one category —
# per agents.md, the match whose keyword appears earliest in the text wins,
# and any multi-match sets flag=NEEDS_REVIEW.
CATEGORY_PATTERNS = [
    ("Pothole", re.compile(r"\bpothole\b", re.I)),
    ("Flooding", re.compile(r"\bflood(ed|ing|s)?\b|waterlog", re.I)),
    ("Drain Blockage", re.compile(r"\bdrain (block|blocked|clogg)", re.I)),
    ("Streetlight", re.compile(r"streetlight|street light|lights? out|flicker|spark", re.I)),
    ("Heritage Damage", re.compile(r"heritage.{0,40}(damage|crumbl|collaps|erod|crack)", re.I)),
    ("Heat Hazard", re.compile(r"\bheat\b|heatwave|extreme temperature", re.I)),
    ("Waste", re.compile(r"garbage|waste|dumped|dead animal|litter", re.I)),
    ("Noise", re.compile(r"\bnoise\b|loud music|playing music", re.I)),
    ("Road Damage", re.compile(r"manhole|footpath|road surface|cracked and sinking|pavement", re.I)),
]

# Severity keywords that force priority=Urgent regardless of category.
# Word-boundary match so "fell" doesn't match "fellow", "child" matches
# "children" (prefix), etc.
SEVERITY_KEYWORDS = re.compile(
    r"\b(injury|injured|child|children|school|hospital|ambulance|fire|hazard|fell|collapse)\w*",
    re.I,
)

REQUIRED_INPUT_COLUMNS = {
    "complaint_id", "date_raised", "city", "ward", "location",
    "description", "reported_by", "days_open",
}


def _match_categories(description: str):
    """Return list of (category, match_start_index) for every category whose
    keyword pattern is found in the description, sorted by where the match
    starts (earliest first)."""
    hits = []
    for category, pattern in CATEGORY_PATTERNS:
        m = pattern.search(description)
        if m:
            hits.append((category, m.start()))
    hits.sort(key=lambda h: h[1])
    return hits


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was empty or unreadable; no signal to classify from.",
            "flag": "NEEDS_REVIEW",
        }

    hits = _match_categories(description)

    if not hits:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f'No known category keyword found in "{description[:80]}"; routed to Other for human review.'
    else:
        category = hits[0][0]
        flag = "NEEDS_REVIEW" if len(hits) > 1 else ""
        reason = f'Classified as {category} based on wording: "{description[:100]}".'

    severity_match = SEVERITY_KEYWORDS.search(description)
    if severity_match:
        priority = "Urgent"
        reason = (
            f'Urgent — description contains severity keyword "{severity_match.group(0)}"; '
            f'category {category} based on: "{description[:80]}".'
        )
    else:
        priority = "Standard"

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
    Never crashes on a bad row: a row that fails to parse still produces an
    output row (category=Other, priority=Low, flag=NEEDS_REVIEW).
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    counts = {"Urgent": 0, "Standard": 0, "Low": 0, "NEEDS_REVIEW": 0}

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001 — batch must never crash
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row failed to parse ({exc}); flagged for manual review.",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow(result)
            counts[result["priority"]] = counts.get(result["priority"], 0) + 1
            if result["flag"] == "NEEDS_REVIEW":
                counts["NEEDS_REVIEW"] += 1

    print(
        f"Classified {sum(v for k, v in counts.items() if k != 'NEEDS_REVIEW')} rows: "
        f"{counts['Urgent']} Urgent, {counts['Standard']} Standard, {counts['Low']} Low "
        f"({counts['NEEDS_REVIEW']} flagged NEEDS_REVIEW)."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
