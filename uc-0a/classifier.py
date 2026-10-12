"""
UC-0A — Complaint Classifier
Built from uc-0a/agents.md (RICE enforcement) and uc-0a/skills.md.

Rule-based and deterministic: the same input always gives the same output,
so every enforcement rule in agents.md can be tested row by row.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Order = precedence when a description matches more than one category.
# The first match is treated as the primary reported problem; the row is
# still flagged NEEDS_REVIEW (agents.md: never be confident on ambiguity).
CATEGORY_PATTERNS = [
    ("Pothole",         [r"\bpot ?holes?\b"]),
    ("Flooding",        [r"\bflood\w*", r"\bwater ?logg\w*", r"\binundat\w*", r"knee-deep"]),
    ("Streetlight",     [r"\bstreet ?lights?\b", r"\blights? out\b", r"\blamp\w*", r"\bunlit\b", r"\bdarkness\b"]),
    ("Heat Hazard",     [r"\bheat\w*", r"\bmelting\b", r"\btemperatures?\b", r"\d+\s?°C"]),
    ("Waste",           [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\brubbish\b", r"\blitter\w*",
                         r"\bdump\w*", r"\bdead animal\b", r"\bcarcass\b", r"\bbins?\b"]),
    ("Noise",           [r"\bnoise\b", r"\bnoisy\b", r"\bmusic\b", r"\bloud\w*", r"\bspeakers?\b",
                         r"\bband playing\b", r"\bdj\b", r"\bdrilling\b", r"\bamplifiers?\b"]),
    ("Road Damage",     [r"\bcrack\w*", r"\bsinking\b", r"\bcaved? in\b", r"\broad surface\b",
                         r"\bfootpath\w*", r"\bpavement\w*", r"\btiles?\b", r"\bmanhole\w*",
                         r"\bcobblestones?\b", r"\bcraters?\b", r"\bsubsid\w*", r"\bpaving\b",
                         r"\bbuckl\w*", r"\bcollaps\w*"]),
    ("Drain Blockage",  [r"\bdrains?\b", r"\bsewer\w*", r"\bgutters?\b", r"\bnala\b"]),
    ("Heritage Damage", [r"\bheritage\b", r"\bhistoric\w*", r"\bmonuments?\b"]),
]

# agents.md enforcement rule 2 — exact list from the UC-0A README, with
# inflections (children, injured, collapsed ...) so "children" is not missed.
SEVERITY_PATTERN = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*|hazard\w*|fell|collapse\w*)\b",
    re.IGNORECASE,
)

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _quote(words):
    return ", ".join(f'"{w}"' for w in words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty, so no category or severity can be determined from it.",
            "flag": "NEEDS_REVIEW",
        }

    # Category evidence: which categories match, and the exact words that matched.
    matches = []
    for category, patterns in CATEGORY_PATTERNS:
        hits = []
        for pattern in patterns:
            for m in re.finditer(pattern, description, re.IGNORECASE):
                if m.group(0) not in hits:
                    hits.append(m.group(0))
        if hits:
            matches.append((category, hits))

    severity_hits = []
    for m in SEVERITY_PATTERN.finditer(description):
        if m.group(0) not in severity_hits:
            severity_hits.append(m.group(0))
    priority = "Urgent" if severity_hits else "Standard"

    if not matches:
        category, flag = "Other", "NEEDS_REVIEW"
        reason = f'No allowed category is supported by the description "{description}"'
    else:
        category, hits = matches[0]
        flag = "NEEDS_REVIEW" if len(matches) > 1 else ""
        reason = f"Classified as {category} because the description says {_quote(hits)}"
        if len(matches) > 1:
            others = "; ".join(f"{c} ({_quote(h)})" for c, h in matches[1:])
            reason += f", but it also matches {others}, so it needs review"

    if severity_hits:
        reason += f", and it is Urgent because it mentions {_quote(severity_hits)}"
    reason += "."

    assert category in ALLOWED_CATEGORIES  # enforcement rule 1: never emit an unlisted label
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
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = {"complaint_id", "description"} - set(reader.fieldnames or [])
            if missing:
                sys.exit(f"Error: input CSV is missing required column(s): {', '.join(sorted(missing))}")
            rows = list(reader)
    except FileNotFoundError:
        sys.exit(f"Error: input file not found: {input_path}")

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # one bad row must never stop the batch
            results.append({
                "complaint_id": (row.get("complaint_id") or "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Row could not be classified ({exc}).",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "rows": len(results),
        "urgent": sum(r["priority"] == "Urgent" for r in results),
        "needs_review": sum(r["flag"] == "NEEDS_REVIEW" for r in results),
    }
    print(f"Classified {summary['rows']} rows: {summary['urgent']} Urgent, "
          f"{summary['needs_review']} flagged NEEDS_REVIEW.")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
