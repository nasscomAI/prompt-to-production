"""
UC-0A — Complaint Classifier

Deterministic, rule-based classifier that enforces the RICE rules from README.md:
  - category is one of a fixed 10-value taxonomy (no variants)
  - priority is Urgent when a severity keyword is present
  - reason cites specific words taken from the description
  - flag is NEEDS_REVIEW when the category is genuinely ambiguous

Run:
  python classifier.py --input ../data/city-test-files/test_hyderabad.csv \
                       --output results_hyderabad.csv
"""
import argparse
import csv
import re

# ── Enforcement constants (mirror agents.md) ──────────────────────────────────

# The ONLY categories allowed in output. Exact strings — no variations.
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Any of these words in the description forces priority = Urgent.
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "hospitalised", "hospitalized",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed",
]

# Ordered category rules. First matching rule wins for the PRIMARY category.
# Each entry: (category, [keywords]). Order encodes precedence for tie-breaks
# where the text plausibly fits more than one bucket.
CATEGORY_RULES = [
    ("Drain Blockage",  ["drain block", "drain completely block", "stormwater drain",
                          "main drain", "drain blocked", "blocked with", "drain 100%"]),
    ("Flooding",        ["flood", "flooded", "waterlog", "knee-deep", "stormwater",
                          "inundat", "submerged", "rainwater"]),
    ("Pothole",         ["pothole", "tyre damage", "tire damage"]),
    ("Road Damage",     ["road collapsed", "road surface cracked", "crater", "sinking",
                          "road damage", "manhole", "footpath", "bridge approach",
                          "cracked and sinking", "partially. crater"]),
    ("Streetlight",     ["streetlight", "street light", "lights out", "light out",
                          "flickering", "sparking", "lights, out"]),
    ("Waste",           ["garbage", "waste", "dumped", "dump", "dead animal",
                          "overflow", "bins", "bulk waste", "not cleared", "not removed"]),
    ("Noise",           ["noise", "music", "drilling", "idling", "loud", "engines on"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat", "heatstroke", "heatwave"]),
]


def _find_category_matches(text: str):
    """Return list of (category, matched_keyword) for every rule that fires."""
    matches = []
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                matches.append((category, kw))
                break  # one keyword hit is enough to score this category
    return matches


def _severity_hits(text: str):
    """Return the severity keywords present in the text (word-boundary aware)."""
    hits = []
    for kw in SEVERITY_KEYWORDS:
        # \b works for alphabetic keywords; keeps 'fell' from matching 'fellow'
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            hits.append(kw)
    return hits


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement:
      - category always drawn from ALLOWED_CATEGORIES
      - priority Urgent iff a severity keyword is present
      - reason cites the actual words that drove the decision
      - flag = NEEDS_REVIEW when the category is genuinely ambiguous
        (no match, or more than one distinct strong category match)
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    text = description.lower()

    # Null / empty description → cannot classify, must be reviewed.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify from an empty field.",
            "flag": "NEEDS_REVIEW",
        }

    matches = _find_category_matches(text)
    distinct_categories = list(dict.fromkeys(c for c, _ in matches))  # dedupe, keep order

    flag = ""
    if not distinct_categories:
        category = "Other"
        matched_kw = None
        flag = "NEEDS_REVIEW"
    else:
        category = distinct_categories[0]  # ordered precedence picks the primary
        matched_kw = next(kw for c, kw in matches if c == category)
        if len(distinct_categories) > 1:
            # Genuinely spans more than one category (e.g. drain blocked AND flooded).
            flag = "NEEDS_REVIEW"

    # Priority via severity keywords.
    sev = _severity_hits(text)
    priority = "Urgent" if sev else "Standard"

    # Build a reason that cites specific words from the description.
    reason_bits = []
    if matched_kw:
        reason_bits.append('matched "%s"' % matched_kw)
    else:
        reason_bits.append("no category keyword matched")
    if len(distinct_categories) > 1:
        reason_bits.append(
            "also matched %s" % ", ".join('"%s"' % c for c in distinct_categories[1:])
        )
    if sev:
        reason_bits.append("severity term(s): " + ", ".join('"%s"' % s for s in sev))

    reason = ("Classified as %s; " % category) + "; ".join(reason_bits) + "."

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

    Robustness: a single bad row never aborts the run — it is captured, flagged
    NEEDS_REVIEW, and output is still produced for every row.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []
    total = 0
    failed = 0

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            try:
                results.append(classify_complaint(row))
            except Exception as exc:  # never let one row kill the batch
                failed += 1
                results.append({
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be classified: %s" % exc,
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    review = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    print("Classified %d rows: %d Urgent, %d NEEDS_REVIEW, %d failed."
          % (total, urgent, review, failed))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
