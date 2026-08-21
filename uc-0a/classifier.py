"""
UC-0A — Complaint Classifier

Rule-driven triage for citizen complaints. Every decision this module makes is
traceable to a rule in agents.md, and every output row carries the words from
the description that drove the decision.

The classification tables below are the executable form of the enforcement
block in agents.md. Changing behaviour means changing a table here and the
matching rule there — not sprinkling special cases through the code.

Run:
    python classifier.py \
      --input ../data/city-test-files/test_hyderabad.csv \
      --output results_hyderabad.csv
"""
import argparse
import csv
import re
import sys

# --- Enforcement rule 1: the category enum is closed --------------------------
# Order matters. It is the deterministic tie-break when two categories score
# equally, and it mirrors the schema table in README.md exactly.
CATEGORIES = [
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

# Signals are matched as word stems: "flood" fires on flooded/flooding/floods.
# PRIMARY (weight 2) names the service directly. SECONDARY (weight 1) is
# circumstantial — on its own it is not enough to classify confidently, which
# is what drives the weak-evidence refusal.
PRIMARY_WEIGHT = 2
SECONDARY_WEIGHT = 1

CATEGORY_SIGNALS = {
    "Pothole": {
        "primary": ["pothole"],
        "secondary": ["tyre damage", "crater 1m"],
    },
    "Flooding": {
        "primary": ["flood", "waterlogg", "inundat", "knee-deep", "knee deep"],
        "secondary": ["rainwater", "stranded", "submerged", "standing in water"],
    },
    "Streetlight": {
        "primary": ["streetlight", "street light", "lamp post", "lamppost", "unlit"],
        "secondary": ["lights out", "flickering", "dark", "wiring", "substation"],
    },
    "Waste": {
        "primary": ["garbage", "waste", "trash", "rubbish", "litter"],
        "secondary": ["dumped", "dead animal", "overflow", "not cleared"],
    },
    "Noise": {
        "primary": ["noise", "music", "drilling", "honking", "amplifier", "loudspeaker"],
        "secondary": ["idling", "past midnight", "5am", "engines on", "audible", "band playing"],
    },
    "Road Damage": {
        "primary": [
            "road collapsed",
            "road surface",
            "crater",
            "manhole",
            "footpath",
            "sinking",
        ],
        "secondary": ["cracked", "tiles broken", "collapse", "depression", "subsidence", "paving"],
    },
    "Heritage Damage": {
        "primary": ["heritage"],
        "secondary": ["old city", "monument"],
    },
    "Heat Hazard": {
        # Heat complaints almost never say "heat hazard". They describe the
        # symptom: a surface melting, a temperature reading, metal too hot to
        # touch. Matching only the label is how this category ends up empty.
        "primary": ["heat", "temperature", "melting", "burns", "full sun", "sunstroke"],
        "secondary": ["bubbling", "no shade", "scorching", "sticking"],
    },
    "Drain Blockage": {
        "primary": ["drain", "stormwater", "sewage"],
        "secondary": ["blocked", "clogged", "mosquito breeding"],
    },
}

# --- Enforcement rule 2: severity terms force Urgent --------------------------
# The left column is the keyword exactly as README.md lists it. The right column
# is the pattern that actually detects it, because the surface forms in the
# complaint text are inflected: "injured", "hospitalised", "collapsed",
# "children". Matching the bare keyword is what causes severity blindness —
# "injury" does not appear in "Child injured last week", so a literal match
# scores that row Standard.
#
# "fell" is deliberately anchored on both sides: an open-ended stem would fire
# on "fellow" and manufacture false Urgents.
SEVERITY_TERMS = [
    ("injury",    r"\binjur\w*"),      # injury, injured, injuries
    ("child",     r"\bchild\w*"),      # child, children
    ("school",    r"\bschool\w*"),
    ("hospital",  r"\bhospital\w*"),   # hospital, hospitalised
    ("ambulance", r"\bambulance\w*"),
    ("fire",      r"\bfire\w*"),
    ("hazard",    r"\bhazard\w*"),     # hazard, hazardous
    ("fell",      r"\bfell\b"),        # past tense only — never "fellow"
    ("collapse",  r"\bcollaps\w*"),    # collapse, collapsed, collapsing
]

# --- Enforcement rule 4: what blocks a Low priority ---------------------------
LOW_ELIGIBLE_CATEGORIES = {"Noise", "Heritage Damage"}
RISK_TERMS = [
    "risk",
    "unsafe",
    "danger",
    "health",
    "injury",
    "blocked",
    "inaccessible",
    "stranded",
]

NEEDS_REVIEW = "NEEDS_REVIEW"
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _find_stem(text: str, term: str):
    """
    Return the actual word from `text` that matched `term`, or None.

    Matching is word-initial and allows a suffix, so the description keeps its
    own wording in the reason field: searching for "hospital" against
    "Rider hospitalised." returns "hospitalised", not "hospital". Multi-word
    terms are matched as phrases.
    """
    pattern = r"\b" + r"\s+".join(re.escape(part) for part in term.split()) + r"\w*"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(0) if match else None


def _score_categories(description: str):
    """
    Score every category against the description.

    Returns {category: (score, [matched words])} for categories that scored.
    """
    scored = {}
    for category, signals in CATEGORY_SIGNALS.items():
        score = 0
        matched = []
        for weight, key in ((PRIMARY_WEIGHT, "primary"), (SECONDARY_WEIGHT, "secondary")):
            for term in signals[key]:
                hit = _find_stem(description, term)
                if hit:
                    score += weight
                    matched.append(hit)
        if score:
            scored[category] = (score, matched)
    return scored


def _detect_severity(description: str):
    """
    Return the severity words present in the description, in README keyword
    order. The word returned is the one the citizen actually wrote, so the
    reason field can quote it.
    """
    hits = []
    for _keyword, pattern in SEVERITY_TERMS:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            hits.append(match.group(0))
    return hits


def _fallback(complaint_id: str, reason: str) -> dict:
    """A row we could not classify still leaves the building — never dropped."""
    return {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": reason,
        "flag": NEEDS_REVIEW,
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Only complaint_id and description are read. reported_by, days_open and ward
    are deliberately ignored — agents.md excludes them from the priority
    decision, so this function must not be able to see them.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return _fallback(complaint_id, "Description field is empty or missing — cannot classify.")

    scored = _score_categories(description)

    # Refusal: no signal at all. The location string is not a fallback source.
    if not scored:
        return _fallback(
            complaint_id,
            "No category signal found in description — needs human categorisation.",
        )

    # Deterministic ranking: score descending, then schema order ascending.
    ranked = sorted(scored.items(), key=lambda kv: (-kv[1][0], CATEGORIES.index(kv[0])))
    category, (top_score, matched) = ranked[0]

    flag = ""
    ambiguity_note = ""

    # Refusal: weak evidence — only a secondary signal fired.
    if top_score < PRIMARY_WEIGHT:
        flag = NEEDS_REVIEW
        ambiguity_note = " Evidence is circumstantial only, so the row is flagged for review."

    # Refusal: a competing category is within half the winning score.
    if len(ranked) > 1:
        runner_up, (runner_score, _) = ranked[1]
        if runner_score >= top_score / 2:
            flag = NEEDS_REVIEW
            ambiguity_note = (
                " Competing category %s also matched, so the row is flagged for review."
                % runner_up
            )

    severity_hits = _detect_severity(description)

    if severity_hits:
        # Overrides everything, including the ambiguity flag.
        priority = "Urgent"
        priority_note = "priority Urgent because severity term '%s' is present" % severity_hits[0]
    elif (
        category in LOW_ELIGIBLE_CATEGORIES
        and not flag
        and not any(_find_stem(description, term) for term in RISK_TERMS)
    ):
        priority = "Low"
        priority_note = "priority Low — amenity complaint with no severity or risk wording"
    else:
        priority = "Standard"
        priority_note = "priority Standard — no severity term in description"

    reason = "Classified %s on '%s'; %s.%s" % (
        category,
        "', '".join(dict.fromkeys(matched)),
        priority_note,
        ambiguity_note,
    )

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

    Produces one output row per input row even when individual rows fail, and
    returns a summary so the run can be audited without opening the file.
    """
    try:
        handle = open(input_path, newline="", encoding="utf-8")
    except OSError as exc:
        raise SystemExit("Cannot read input file %s: %s" % (input_path, exc))

    with handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "description" not in reader.fieldnames:
            raise SystemExit(
                "Input %s has no 'description' column — refusing to emit 'Other' for every row."
                % input_path
            )
        rows = list(reader)

    results = []
    failed = 0
    for index, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:  # one bad row must not truncate the file
            failed += 1
            result = _fallback("", "Row failed during classification: %s" % exc)
        if not result["complaint_id"]:
            result["complaint_id"] = "ROW_%d" % index
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    tally = {}
    for result in results:
        tally[result["category"]] = tally.get(result["category"], 0) + 1

    return {
        "rows_in": len(rows),
        "rows_out": len(results),
        "failed_rows": failed,
        "urgent_count": sum(1 for r in results if r["priority"] == "Urgent"),
        "needs_review_count": sum(1 for r in results if r["flag"] == NEEDS_REVIEW),
        "by_category": dict(sorted(tally.items())),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    summary = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
    print(f"  rows in/out       : {summary['rows_in']}/{summary['rows_out']}")
    print(f"  urgent            : {summary['urgent_count']}")
    print(f"  needs review      : {summary['needs_review_count']}")
    print(f"  failed rows       : {summary['failed_rows']}")
    for name, count in summary["by_category"].items():
        print(f"  {name:<16}: {count}")
    if summary["rows_in"] != summary["rows_out"]:
        sys.exit("Row count mismatch — output is incomplete.")
