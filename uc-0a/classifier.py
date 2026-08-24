"""
UC-0A — Complaint Classifier

Every rule in uc-0a/agents.md is implemented here as executable enforcement, so that
"the AI followed the rule" is a thing a reviewer can verify by running the file rather
than a thing they have to trust.

Run:
    python3 classifier.py --input ../data/city-test-files/test_pune.csv \
                          --output results_pune.csv
"""
import argparse
import csv
import re
import sys

# --- Enforcement 1: closed taxonomy. Exact strings, no variants, no sub-categories. ---
CATEGORIES = (
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
)

# --- Enforcement 2: severity terms that force Urgent. -------------------------------
# Word-boundary patterns, not substrings: "fell" must not fire on "fellow" and "fire"
# must not fire on "firearm", while "child" must still fire on "children".
SEVERITY_PATTERNS = {
    "injury": r"\binjur(?:y|ies|ed)\b",
    "child": r"\bchild(?:ren)?\b",
    "school": r"\bschools?\b",
    "hospital": r"\bhospitals?\b",
    "ambulance": r"\bambulances?\b",
    "fire": r"\bfires?\b",
    "hazard": r"\bhazard(?:s|ous)?\b",
    "fell": r"\bfell\b",
    "collapse": r"\bcollapse[ds]?\b",
}

# --- Enforcement 5: a signal counts only when it names the DEFECT, not the setting. --
# "Karve Road" is a location; "road surface cracked" is a defect. Hence no bare \broad\b
# and no bare \bheritage\b — those would classify the backdrop instead of the complaint.
CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpot[- ]?holes?\b",
    ],
    "Flooding": [
        r"\bflood(?:ed|ing|s)?\b",
        r"\bwaterlogg\w*\b",
        r"\bknee[- ]deep\b",
        r"\bstanding in water\b",
        r"\binundat\w+\b",
    ],
    "Streetlight": [
        r"\bstreet[- ]?lights?\b",
        r"\bstreet[- ]?lamps?\b",
        r"\blights? (?:out|not working|off)\b",
        r"\blight(?:s)? (?:flickering|fused)\b",
    ],
    "Waste": [
        r"\bgarbage\b", r"\bwaste\b", r"\brubbish\b", r"\btrash\b",
        r"\bdead animal\b", r"\bdumped\b", r"\bdumping\b",
        r"\bbins?\b", r"\blitter\w*\b",
    ],
    "Noise": [
        r"\bnoise\b", r"\bmusic\b", r"\bloudspeaker\w*\b",
        r"\bpast midnight\b", r"\bblaring\b",
    ],
    "Road Damage": [
        r"\bfootpath\w*\b",
        r"\bcrack(?:ed|s|ing)?\b",
        r"\bsinking\b", r"\bsubsidence\b", r"\bsunken\b",
        r"\bmanhole cover (?:missing|open|broken|damaged)\b",
        r"\bmissing manhole cover\b",
        r"\broad surface\b",
        r"\btiles? (?:broken|upturned|damaged)\b",
    ],
    "Heritage Damage": [
        # Heritage word AND a damage verb, in either order, within one sentence.
        r"\b(?:heritage|monument\w*|historic\w*)\b[^.]{0,80}?\b(?:damag\w+|defac\w+|vandal\w+|crumbl\w+|collaps\w+)\b",
        r"\b(?:damag\w+|defac\w+|vandal\w+|crumbl\w+|collaps\w+)\b[^.]{0,80}?\b(?:heritage|monument\w*|historic\w*)\b",
    ],
    "Heat Hazard": [
        r"\bheat[- ]?wave\b", r"\bheat hazard\b", r"\bheatstroke\b",
        r"\bno shade\b", r"\bextreme heat\b",
    ],
    "Drain Blockage": [
        r"\bdrains?\s+(?:blocked|choked|clogged|overflow\w*)\b",
        r"\bblocked drains?\b", r"\bchoked drains?\b",
        r"\bdrainage\s+(?:blocked|choked|clogged)\b",
        r"\bsewage\b",
        r"\bmanhole\s+(?:blocked|choked|overflow\w*)\b",
    ],
}


def _find_severity(description: str):
    """Return [(term, matched_literal_text), ...] for every severity term present."""
    hits = []
    for term, pattern in SEVERITY_PATTERNS.items():
        m = re.search(pattern, description, re.IGNORECASE)
        if m:
            hits.append((term, m.group(0)))
    return hits


def _find_categories(description: str):
    """
    Return [(category, first_match_position, matched_literal_text, n_patterns), ...]
    sorted by the order the evidence appears in the text.
    """
    found = []
    for category, patterns in CATEGORY_PATTERNS.items():
        matches = [m for p in patterns
                   for m in [re.search(p, description, re.IGNORECASE)] if m]
        if matches:
            first = min(matches, key=lambda m: m.start())
            found.append((category, first.start(), first.group(0), len(matches)))
    found.sort(key=lambda t: t[1])
    return found


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement applied here, in order:
      - closed taxonomy (never an invented category)
      - severity terms force Urgent, overriding everything else
      - reason always quotes a literal phrase from this row's description
      - two competing defect phrases -> first-mentioned wins + NEEDS_REVIEW
      - no match or no description -> Other + NEEDS_REVIEW, never a guess
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Enforcement 7: refusal condition. No text means no determination.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description field is empty or missing, so no category can be determined from the description alone.",
            "flag": "NEEDS_REVIEW",
        }

    severity = _find_severity(description)
    candidates = _find_categories(description)

    if not candidates:
        # Enforcement 7 again: refuse rather than reach for the nearest-looking bucket.
        priority = "Urgent" if severity else "Standard"
        cited = severity[0][1] if severity else description.split(".")[0][:60]
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f"No permitted category is named in the description; cannot classify "
                f"from \"{cited}\" alone."
            ),
            "flag": "NEEDS_REVIEW",
        }

    # Enforcement 6: first-mentioned defect wins; the runner-up is never discarded.
    category, _pos, cited_phrase, _n = candidates[0]
    competing = [c for c, _p, _t, _n in candidates[1:]]

    # Enforcement 2 + 3: severity decides priority. days_open and reported_by are
    # deliberately never read in this function.
    if severity:
        priority = "Urgent"
        terms = ", ".join(f"\"{text}\"" for _term, text in severity)
        priority_clause = f"priority Urgent because the description contains {terms}"
    else:
        priority = "Standard"
        priority_clause = "priority Standard as no severity term is present"

    # Enforcement 4: the reason quotes the description verbatim.
    reason = f"Category {category} from the phrase \"{cited_phrase}\"; {priority_clause}."
    flag = ""
    if competing:
        flag = "NEEDS_REVIEW"
        reason += (
            f" Ambiguous: {' and '.join(competing)} also explicitly evidenced in the "
            f"same description."
        )

    assert category in CATEGORIES, f"taxonomy violation: {category}"
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, classify each row, write results CSV.

    Fails fast on a missing file or a missing description column — an empty results
    file is a worse outcome than a loud error. Never fails on a single bad row: that
    row is emitted as Other / NEEDS_REVIEW so rows_out always equals rows_in.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        sys.exit(f"ERROR: input file not found: {input_path}")

    if not rows:
        sys.exit(f"ERROR: input file has no data rows: {input_path}")
    if "description" not in rows[0]:
        sys.exit(
            f"ERROR: input file has no 'description' column (found: "
            f"{', '.join(rows[0].keys())})"
        )

    results, failed = [], []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # one bad row must not cost the batch
            failed.append((row.get("complaint_id", "<no id>"), repr(exc)))
            results.append({
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row could not be processed ({exc.__class__.__name__}); "
                          f"emitted for manual triage rather than dropped.",
                "flag": "NEEDS_REVIEW",
            })

    fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    # Enforcement 1/e: no row may be dropped.
    assert len(results) == len(rows), "row count mismatch — a complaint was lost"

    return {
        "rows_in": len(rows),
        "rows_out": len(results),
        "urgent": sum(1 for r in results if r["priority"] == "Urgent"),
        "flagged": sum(1 for r in results if r["flag"] == "NEEDS_REVIEW"),
        "failed_rows": failed,
        "by_category": {c: sum(1 for r in results if r["category"] == c)
                        for c in CATEGORIES
                        if any(r["category"] == c for r in results)},
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0A municipal complaint classifier")
    parser.add_argument("--input", required=True, help="path to test_[city].csv")
    parser.add_argument("--output", required=True, help="path to results_[city].csv")
    args = parser.parse_args()

    summary = batch_classify(args.input, args.output)

    print(f"Wrote {args.output}")
    print(f"  rows in / out : {summary['rows_in']} / {summary['rows_out']}")
    print(f"  urgent        : {summary['urgent']}")
    print(f"  needs review  : {summary['flagged']}")
    for category, count in summary["by_category"].items():
        print(f"    {category:<16} {count}")
    if summary["failed_rows"]:
        print("  rows that failed classification (still written as Other):")
        for cid, err in summary["failed_rows"]:
            print(f"    {cid}: {err}")


if __name__ == "__main__":
    main()
