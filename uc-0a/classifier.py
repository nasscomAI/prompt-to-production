"""
UC-0A — Complaint Classifier

Classifies citizen complaints from a city test CSV into the exact taxonomy
defined in README.md. Produces results_[city].csv with columns:
complaint_id, category, priority, reason, flag.

Enforcement rules (from agents.md) implemented here:
  1. category is ALWAYS one of the 10 allowed strings.
  2. priority is Urgent iff a severity keyword appears in the description.
  3. every output row includes a reason field citing words from the description.
  4. genuinely ambiguous / unmatchable complaints -> category Other (or best
     match) and flag NEEDS_REVIEW; never a confident guess on ambiguity.
"""
import argparse
import csv
import os
import re
import sys

# ---------------------------------------------------------------------------
# Taxonomy — exact strings only, no variations.
# ---------------------------------------------------------------------------
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
    "injury",
    "child",
    "children",
    "school",
    "hospital",
    "hospitalised",
    "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
]

# Keyword rules per category. Each entry is (keyword, weight). Matching is done
# case-insensitively with word boundaries against the lower-cased description,
# so "hot" never matches inside "photographing" and "water" never matches
# inside "rainwater".
CATEGORY_RULES = {
    "Pothole": [
        ("pothole", 3),
        ("potholes", 3),
        ("pot hole", 3),
    ],
    "Flooding": [
        ("flooded", 4),
        ("flooding", 3),
        ("flood", 3),
        ("floods", 3),
        ("waterlogging", 3),
        ("water logged", 3),
        ("inundated", 3),
        ("inundation", 3),
        ("submerged", 3),
        ("knee-deep", 3),
        ("rainwater", 1),
        ("rainfall", 1),
        ("water", 1),
        ("rain", 1),
    ],
    "Streetlight": [
        ("lights out", 3),
        ("light out", 3),
        ("streetlight", 3),
        ("street lights", 3),
        ("street light", 3),
        ("lamp post", 3),
        ("lamppost", 3),
        ("unlit", 2),
        ("darkness", 2),
        ("dark", 2),
        ("substation", 2),
        ("sparking", 2),
        ("flickering", 2),
        ("tripped", 2),
    ],
    "Waste": [
        ("garbage", 3),
        ("rubbish", 3),
        ("dead animal", 3),
        ("waste", 2),
        ("litter", 2),
        ("overflowing", 2),
        ("bins", 2),
        ("dump", 2),
        ("dumped", 2),
        ("not cleared", 2),
        ("piles", 2),
        ("unusable", 2),
    ],
    "Noise": [
        ("music", 3),
        ("amplifiers", 3),
        ("amplifier", 3),
        ("wedding band", 3),
        ("drilling", 3),
        ("idling", 3),
        ("noise", 2),
        ("noisy", 2),
        ("loud", 2),
        ("band", 2),
        ("club", 2),
        ("engine", 2),
        ("engines", 2),
    ],
    "Road Damage": [
        ("manhole", 3),
        ("footpath", 3),
        ("road surface", 2),
        ("cracked", 2),
        ("sinking", 2),
        ("subsidence", 2),
        ("subsided", 2),
        ("buckled", 2),
        ("crater", 2),
        ("collapsed", 2),
        ("cobblestones", 2),
        ("paving", 2),
        ("gas pipeline", 2),
        ("gas leak", 2),
        ("tiles", 2),
        ("road", 1),
    ],
    "Heritage Damage": [
        ("heritage", 3),
        ("historic", 3),
        ("ancient", 3),
        ("monument", 3),
        ("defaced", 3),
        ("step well", 2),
        ("museum", 1),
    ],
    "Heat Hazard": [
        ("heatwave", 3),
        ("melting", 3),
        ("burns", 3),
        ("storing heat", 3),
        ("unbearable", 3),
        ("44\u00b0c", 3),
        ("45\u00b0c", 3),
        ("52\u00b0c", 3),
        ("heat", 2),
        ("hot", 2),
        ("temperature", 2),
        ("temperatures", 2),
        ("sun", 2),
        ("warm", 2),
    ],
    "Drain Blockage": [
        ("stormwater", 3),
        ("sewage", 3),
        ("mosquito", 3),
        ("drain", 2),
        ("draining", 2),
        ("drainage", 2),
        ("blocked", 2),
        ("block", 2),
        ("culvert", 2),
    ],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

# Pre-compile word-boundary regexes.
_PATTERNS = {}
for _cat, _rules in CATEGORY_RULES.items():
    _PATTERNS[_cat] = [(kw, w, re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
                       for kw, w in _rules]
_SEVERITY_PATTERNS = [(kw, re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
                      for kw in SEVERITY_KEYWORDS]


def _match_keywords(low: str, category: str) -> tuple:
    """Return (score, matched_keyword_list) for one category against text."""
    score = 0
    matched = []
    for kw, weight, pattern in _PATTERNS[category]:
        if pattern.search(low):
            score += weight
            matched.append(kw)
    return score, matched


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    """
    description = (row.get("description") or "").strip()
    low = description.lower()

    scores = {}
    matched_terms = {}
    for category in ALLOWED_CATEGORIES:
        if category == "Other":
            continue
        score, terms = _match_keywords(low, category)
        if score > 0:
            scores[category] = score
            matched_terms[category] = terms

    if not scores:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No classification keyword matched the description; category cannot be determined from description alone."
    else:
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], ALLOWED_CATEGORIES.index(kv[0])))
        top_category, top_score = ranked[0]
        category = top_category

        second_score = ranked[1][1] if len(ranked) > 1 else 0
        ambiguous = second_score >= 2
        flag = "NEEDS_REVIEW" if ambiguous else ""

        cited = matched_terms[top_category][:4]
        quote = ", ".join('"%s"' % c for c in cited)
        reason = "Description mentions %s." % quote
        if ambiguous:
            other = [c for c, _ in ranked[1:] if c != category][:2]
            reason += " Also matches %s; category is ambiguous." % ", ".join(other)

    # Priority: Urgent iff any severity keyword appears in the description.
    severity = [kw for kw, pattern in _SEVERITY_PATTERNS if pattern.search(low)]
    priority = "Urgent" if severity else "Standard"
    if severity:
        reason = "%s Severity keyword \"%s\" present -> Urgent." % (reason, severity[0])

    return {
        "complaint_id": (row.get("complaint_id") or "").strip(),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Never crashes on bad rows — malformed rows are classified as Other with
    NEEDS_REVIEW so the output is always produced.
    """
    if not os.path.isfile(input_path):
        print("Error: input file not found: %s" % input_path, file=sys.stderr)
        sys.exit(1)

    rows = []
    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                rows.append(raw)
    except Exception as exc:
        print("Error reading %s: %s" % (input_path, exc), file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Error: input file contains no data rows.", file=sys.stderr)
        sys.exit(1)

    results = []
    failed = 0
    for raw in rows:
        try:
            result = classify_complaint(raw)
        except Exception as exc:
            failed += 1
            result = {
                "complaint_id": (raw.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": "Malformed row (%s); could not be classified." % exc,
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print("Classified %d row(s) -> %s (failed rows: %d)" % (len(results), output_path, failed))
    print("NEEDS_REVIEW rows: %d" % sum(1 for r in results if r["flag"] == "NEEDS_REVIEW"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)