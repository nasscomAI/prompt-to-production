"""
UC-0A — Complaint Classifier

Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

Every rule below is a direct implementation of an enforcement clause in
uc-0a/agents.md. The classification is deterministic and keyword-evidenced:
each decision can be re-derived from the reason field alone, and no network
call or model inference is involved, so the enforcement rules are testable.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv \
                         --output results_pune.csv
"""
import argparse
import csv
import os
import re
import sys
from collections import Counter

# --- Enforcement rule 1: the taxonomy is a closed set -----------------------
# Order is the deterministic tie-break order, most-specific defect first.
# A tie between two categories is never resolved silently -- it is resolved by
# this order AND flagged NEEDS_REVIEW (enforcement rule 5).
CATEGORY_KEYWORDS = [
    ("Pothole", [
        "pothole", "potholes", "pot hole", "road pit", "crater",
    ]),
    ("Flooding", [
        "flood", "floods", "flooded", "flooding", "waterlogged",
        "waterlogging", "knee-deep", "knee deep", "submerged",
        "standing in water", "inundated", "rainwater", "water enters",
    ]),
    ("Streetlight", [
        "streetlight", "streetlights", "street light", "street lights",
        "lights out", "light out", "lamp post", "lamppost", "street lamp",
        "no lighting", "unlit", "substation", "darkness", "blackout",
        "power cut", "no power",
    ]),
    ("Road Damage", [
        "road surface", "road damage", "footpath", "pavement", "sidewalk",
        "cracked", "sinking", "caved", "crumbling", "manhole cover",
        "tiles broken", "broken tiles", "upturned", "subsidence",
        "subsided", "subsiding", "tarmac", "asphalt", "speed breaker",
        "divider", "road caved",
    ]),
    ("Drain Blockage", [
        "drain", "drains", "drainage", "draining", "drained", "manhole",
        "sewer", "sewage", "gutter", "nala", "choked", "culvert",
        "storm water", "stormwater",
    ]),
    ("Waste", [
        "garbage", "waste", "trash", "rubbish", "litter", "dead animal",
        "bins", "bin", "dumped", "debris", "malba",
    ]),
    ("Noise", [
        "noise", "music", "loudspeaker", "loud speaker", "blaring", "dj",
        "honking", "amplifier", "drilling", "drill", "band", "idling",
        "hammering", "generator", "firecracker", "firecrackers", "5am",
    ]),
    ("Heritage Damage", [
        "heritage", "monument", "historic", "historical", "wada",
        "fort", "archaeological", "museum", "statue", "old city",
    ]),
    ("Heat Hazard", [
        "heat", "heatwave", "heat wave", "sunstroke", "no shade",
        "scorching", "temperature", "temperatures", "melting", "melts",
        "sun", "full sun", "44°c", "°c", "shade",
    ]),
]

ALLOWED_CATEGORIES = [name for name, _ in CATEGORY_KEYWORDS] + ["Other"]

# --- Enforcement rule 2: severity overrides everything ----------------------
# The nine severity keywords from the UC-0A README, plus the inflections that
# actually occur in complaint text. This check is independent of category, so
# an unclassifiable injury complaint is still Urgent.
SEVERITY_TERMS = [
    "injury", "injured", "injuries",
    "child", "children",
    "school", "schools",
    "hospital", "hospitals",
    "ambulance", "ambulances",
    "fire",
    "hazard", "hazardous", "hazards",
    "fell", "fallen", "fall", "falls", "falling",
    "collapse", "collapsed", "collapsing",
]

# --- Enforcement rule 3: Low requires the absence of any impact signal ------
IMPACT_TERMS = [
    "flood", "floods", "flooded", "flooding", "block", "blocked", "blockage",
    "stranded", "overflow", "overflowing", "dark", "health", "risk",
    "damage", "damaged", "missing", "broken", "sinking", "cracked",
    "dumped", "dead", "smell", "inaccessible", "sparking", "stagnant",
    "leak", "leaking", "unsafe", "accident", "darkness", "dangerous",
    "danger", "exposed", "trapped", "stuck", "suspended", "refusing",
    "not removed", "obstruction", "overflowed",
]

# Low is never the fallback. It is reserved for nuisance-class categories that
# also show no impact evidence, so that an unrecognised word can only ever cost
# a row its Low rating -- never downgrade a safety complaint to Low.
LOW_ELIGIBLE_CATEGORIES = {"Noise"}

# A runner-up category within this many keyword hits of the leader counts as
# genuine ambiguity and forces NEEDS_REVIEW (enforcement rule 5).
AMBIGUITY_MARGIN = 1

PRIORITY_URGENT = "Urgent"
PRIORITY_STANDARD = "Standard"
PRIORITY_LOW = "Low"

FLAG_REVIEW = "NEEDS_REVIEW"
FLAG_NONE = ""

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _find_terms(text, terms):
    """Return the literal matched substrings, in the casing used by the source.

    Whole-word matching only, so 'bin' does not fire inside 'binding' and
    'fire' does not fire inside 'firewall'. The matched text is captured from
    the original description so the reason field quotes the citizen's own
    words (enforcement rule 4).
    """
    found = []
    seen = set()
    for term in terms:
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(0).lower() not in seen:
            seen.add(match.group(0).lower())
            found.append(match.group(0))
    return found


def _quote(terms):
    return ", ".join("'%s'" % t for t in terms)


def classify_complaint(row):
    """Classify a single complaint row.

    Returns: dict with keys complaint_id, category, priority, reason, flag.

    Never raises and never returns None -- a row that cannot be classified is
    still a row that must be reported (skills.md: classify_complaint
    error_handling).
    """
    row = row or {}
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Enforcement rule 6: a null row is reported, never dropped.
    null_fields = []
    if not complaint_id:
        complaint_id = "UNKNOWN_ID"
        null_fields.append("complaint_id")
    if not description:
        null_fields.append("description")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": PRIORITY_STANDARD,
            "reason": (
                "Cannot classify: required field(s) %s are null or empty in the "
                "source row, so no description text exists to cite as evidence."
                % _quote(null_fields)
            ),
            "flag": FLAG_REVIEW,
        }

    # --- Category: score every category by distinct keyword evidence --------
    scores = []
    for category, keywords in CATEGORY_KEYWORDS:
        hits = _find_terms(description, keywords)
        if hits:
            scores.append((len(hits), category, hits))

    if not scores:
        # Enforcement rule 5: no keyword match -> Other + NEEDS_REVIEW.
        # The agent never mints a new category name to fit the text.
        category = "Other"
        category_hits = []
        flag = FLAG_REVIEW
        category_clause = (
            "no term in the closed taxonomy matched the description, so category "
            "defaults to Other"
        )
    else:
        top_score = max(s[0] for s in scores)
        # The winner is always drawn from the highest-scoring group;
        # CATEGORY_KEYWORDS order is the documented tie-break within it.
        leaders = [s for s in scores if s[0] == top_score]
        _, category, category_hits = leaders[0]
        # Enforcement rule 5: a rival category with COMPARABLE evidence is
        # genuine ambiguity, not just an exact tie. Keyword count measures
        # vocabulary overlap, not diagnostic certainty -- "Bus stand flooded,
        # drain blocked" leads Flooding 2:1 while still being a real
        # Flooding/Drain Blockage judgement call. AMBIGUITY_MARGIN is the
        # width of that doubt. Rivals never displace the leader; they only
        # force the flag.
        rivals = [s for s in scores
                  if s[1] != category and top_score - s[0] <= AMBIGUITY_MARGIN]
        if rivals:
            flag = FLAG_REVIEW
            rival_names = [c[1] for c in rivals]
            category_clause = (
                "category %s chosen from matched term(s) %s, but %s also matched "
                "on comparable evidence"
                % (category, _quote(category_hits), " and ".join(rival_names))
            )
        else:
            flag = FLAG_NONE
            category_clause = (
                "category %s from matched term(s) %s"
                % (category, _quote(category_hits))
            )

    # --- Priority: severity check runs first and overrides ------------------
    severity_hits = _find_terms(description, SEVERITY_TERMS)
    impact_hits = _find_terms(description, IMPACT_TERMS)

    if severity_hits:
        priority = PRIORITY_URGENT
        priority_clause = (
            "priority Urgent because the description contains severity term(s) %s"
            % _quote(severity_hits)
        )
    elif impact_hits:
        priority = PRIORITY_STANDARD
        priority_clause = (
            "priority Standard because no severity term is present but impact "
            "term(s) %s are" % _quote(impact_hits)
        )
    elif category in LOW_ELIGIBLE_CATEGORIES:
        priority = PRIORITY_LOW
        priority_clause = (
            "priority Low because %s is a nuisance-class category and neither a "
            "severity nor an impact term appears in the description" % category
        )
    else:
        priority = PRIORITY_STANDARD
        priority_clause = (
            "priority Standard by default because %s is not a nuisance-class "
            "category, so absence of matched impact vocabulary cannot justify a "
            "downgrade to Low" % category
        )

    reason = "%s; %s." % (category_clause, priority_clause)
    if flag == FLAG_REVIEW and scores:
        reason = reason[:-1] + "; flagged NEEDS_REVIEW for human confirmation."
    elif flag == FLAG_REVIEW:
        reason = reason[:-1] + "; flagged NEEDS_REVIEW."

    if null_fields:
        flag = FLAG_REVIEW
        reason = reason[:-1] + (
            "; null field(s) %s reported." % _quote(null_fields)
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    """Read input CSV, classify each row, write results CSV.

    Flags nulls before computing, does not crash on a bad row, and produces
    output even if some rows fail (skills.md: batch_classify error_handling).
    """
    if not os.path.isfile(input_path):
        raise SystemExit("ERROR: input file not found: %s" % input_path)

    try:
        handle = open(input_path, "r", newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise SystemExit("ERROR: cannot read %s (%s)" % (input_path, exc))

    with handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [c for c in ("complaint_id", "description")
                   if c not in fieldnames]
        if missing:
            raise SystemExit(
                "ERROR: input is missing required column(s) %s. Columns found: %s"
                % (", ".join(missing), ", ".join(fieldnames) or "(none)")
            )
        rows = list(reader)

    # --- Null report BEFORE classification, so nulls are visible ------------
    null_report = []
    for index, row in enumerate(rows, start=1):
        empties = [k for k in fieldnames if not (row.get(k) or "").strip()]
        if empties:
            null_report.append((index, row.get("complaint_id") or "UNKNOWN_ID",
                                empties))

    print("Input:  %s" % input_path)
    print("Rows read: %d" % len(rows))
    if null_report:
        print("NULL REPORT — %d row(s) contain empty fields:" % len(null_report))
        for index, cid, empties in null_report:
            print("  row %d (%s): %s" % (index, cid, ", ".join(empties)))
    else:
        print("NULL REPORT — no empty fields detected.")

    results = []
    for index, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:  # one bad row never costs the others
            result = {
                "complaint_id": (row.get("complaint_id") or "UNKNOWN_ID"),
                "category": "Other",
                "priority": PRIORITY_STANDARD,
                "reason": (
                    "Row %d could not be classified due to an unexpected error: "
                    "%s." % (index, exc)
                ),
                "flag": FLAG_REVIEW,
            }
        # Guard: never emit a value outside the closed taxonomy.
        if result["category"] not in ALLOWED_CATEGORIES:
            result["category"] = "Other"
            result["flag"] = FLAG_REVIEW
        results.append(result)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    with open(output_path, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "total_rows": len(results),
        "urgent_count": sum(1 for r in results
                            if r["priority"] == PRIORITY_URGENT),
        "standard_count": sum(1 for r in results
                              if r["priority"] == PRIORITY_STANDARD),
        "low_count": sum(1 for r in results if r["priority"] == PRIORITY_LOW),
        "needs_review_count": sum(1 for r in results
                                  if r["flag"] == FLAG_REVIEW),
        "null_field_rows": len(null_report),
        "per_category": dict(Counter(r["category"] for r in results)),
    }

    print("")
    print("RUN SUMMARY")
    print("  rows written    : %d" % summary["total_rows"])
    print("  Urgent          : %d" % summary["urgent_count"])
    print("  Standard        : %d" % summary["standard_count"])
    print("  Low             : %d" % summary["low_count"])
    print("  NEEDS_REVIEW    : %d" % summary["needs_review_count"])
    print("  rows with nulls : %d" % summary["null_field_rows"])
    print("  by category     :")
    for name in ALLOWED_CATEGORIES:
        if name in summary["per_category"]:
            print("      %-16s %d" % (name, summary["per_category"][name]))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)
