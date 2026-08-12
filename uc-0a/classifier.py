"""
UC-0A — Complaint Classifier

Deterministic, offline triage of civic complaints. No network, no model call:
every decision is a rule that a reviewer can re-derive by hand from agents.md.

Design notes (these are the enforcement rules from agents.md, in code):
  * Category comes from a CLOSED taxonomy of 10 strings. A label that is not in
    ALLOWED_CATEGORIES cannot leave this module.
  * Evidence is two-tier. STRONG evidence names the complaint type outright
    ("pothole", "manhole"); WEAK evidence only corroborates ("knee-deep",
    "blocked"). Weak evidence never outvotes strong evidence.
  * Ambiguity is detected, not resolved. Two categories with strong evidence
    means the row describes two complaint types, so it is flagged for a human
    instead of being silently forced into one bucket.
  * Severity is checked AFTER the category and can only raise priority.
  * `days_open` and `reported_by` are deliberately never read. Complaint age is
    a backlog metric, and escalating by reporter channel is political bias.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv \
                         --output results_pune.csv
"""
import argparse
import csv
import io
import os
import re
import sys
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Taxonomy — closed set. Enforcement rule 1.
# ─────────────────────────────────────────────────────────────────────────────
ALLOWED_CATEGORIES = (
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
)

FALLBACK_CATEGORY = "Other"
REVIEW_FLAG = "NEEDS_REVIEW"
OUTPUT_FIELDS = ("complaint_id", "category", "priority", "reason", "flag")

# ─────────────────────────────────────────────────────────────────────────────
# Category evidence. "strong" = names the complaint type. "weak" = corroborates.
# All patterns are word-boundary anchored so `fell` never fires on `fellow`.
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_EVIDENCE = {
    "Pothole": {
        "strong": [r"pot\s?holes?", r"craters?"],
        "weak": [r"tyre damage", r"vehicle damage"],
    },
    "Flooding": {
        "strong": [r"flood\w*", r"water[\s-]?logg\w*", r"inundat\w*", r"submerged"],
        "weak": [
            r"knee[\s-]deep",
            r"standing in water",
            r"stranded",
            r"waist[\s-]deep",
            r"rain\s?water",
        ],
    },
    "Streetlight": {
        "strong": [
            r"street\s?lights?",
            r"street\s?lamps?",
            r"street\s?lighting",
            r"lights? out",
            r"lamp\s?posts?",
            r"unlit",
        ],
        "weak": [
            r"very dark",
            r"dark at night",
            r"after dark",
            r"flickering",
            r"darkness",
            r"substation",
            r"wiring",
        ],
    },
    "Waste": {
        "strong": [
            r"garbage",
            r"wastes?",
            r"trash",
            r"rubbish",
            r"litter\w*",
            r"dead animals?",
            r"dumped",
            r"dumping",
        ],
        "weak": [r"bins?", r"smell\w*", r"debris", r"unhygienic"],
    },
    "Noise": {
        "strong": [
            r"noise",
            r"loud\w*",
            r"music",
            r"loud\s?speakers?",
            r"\bdj\b",
            r"drilling",
            r"\bbands?\b",
        ],
        "weak": [
            r"past midnight",
            r"honking",
            r"late night",
            r"idling",
            r"engines? on",
            r"fire\s?crackers?",
            r"horns?",
        ],
    },
    "Road Damage": {
        "strong": [
            r"road surface",
            r"cracked",
            r"sinking",
            r"subsid\w*",
            r"caved[\s-]?in",
            r"foot\s?paths?",
            r"pavements?",
            r"paving",
            r"cobble\s?stones?",
            r"tarmac",
            r"tiles broken",
            r"broken tiles",
            r"road damage",
        ],
        "weak": [r"upturned", r"uneven", r"utility work"],
    },
    "Heritage Damage": {
        "strong": [
            r"heritage",
            r"monuments?",
            r"historical?",
            r"museums?",
            r"ancient",
            r"step\s?well",
            r"\bwada\b",
            r"\bfort\b",
        ],
        "weak": [r"old city", r"conservation"],
    },
    "Heat Hazard": {
        "strong": [
            r"heat\s?waves?",
            r"\bheat\b",
            r"extreme temperature",
            r"temperatures?",
            r"melting",
            r"\d+\s*°\s*c",
        ],
        "weak": [
            r"no shade",
            r"tree cover",
            r"drinking water shortage",
            r"unbearable",
            r"full sun",
        ],
    },
    "Drain Blockage": {
        "strong": [r"drain\w*", r"sewers?", r"sewage", r"man\s?holes?", r"nalla", r"gutters?"],
        "weak": [r"blocked", r"choked", r"clogged", r"overflow\w*", r"backflow"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Severity stems — enforcement rule 2. Word-boundary anchored (rule 3).
# `fell` is exact-word only: "Elderly resident fell" fires, "fellow" does not.
# ─────────────────────────────────────────────────────────────────────────────
SEVERITY_PATTERNS = {
    "injury": r"\binjur\w*\b",
    "child": r"\bchild\w*\b",
    "school": r"\bschool\w*\b",
    "hospital": r"\bhospital\w*\b",
    "ambulance": r"\bambulance\w*\b",
    "fire": r"\bfires?\b",
    "hazard": r"\bhazard\w*\b",
    "fell": r"\bfell\b",
    "collapse": r"\bcollaps\w*\b",
}

# Priority Low is reserved for Noise with no severity signal — the only category
# with no safety dimension at all. Everything else defaults to Standard, so Low
# always means "genuinely deferrable" and never "the classifier was unsure".
LOW_PRIORITY_CATEGORIES = ("Noise",)


def _find_matches(text: str, patterns: List[str]) -> List[str]:
    """Return the literal substrings of `text` matched by `patterns`.

    Returning the matched text (not the pattern) is what lets every reason cite
    words that are verifiably present in the description.
    """
    found = []
    for pattern in patterns:
        match = re.search(r"\b" + pattern + r"\b", text, re.IGNORECASE)
        if match:
            term = match.group(0).strip()
            if term and term.lower() not in [f.lower() for f in found]:
                found.append(term)
    return found


def _score_categories(description: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Collect strong and weak evidence per category. No decision made here."""
    strong = {}
    weak = {}
    for category, evidence in CATEGORY_EVIDENCE.items():
        strong_hits = _find_matches(description, evidence["strong"])
        weak_hits = _find_matches(description, evidence["weak"])
        if strong_hits:
            strong[category] = strong_hits
        if weak_hits:
            weak[category] = weak_hits
    return strong, weak


def _detect_severity(description: str) -> List[Tuple[str, str]]:
    """Return (stem_name, literal_matched_text) for every severity stem present."""
    hits = []
    for stem, pattern in SEVERITY_PATTERNS.items():
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            hits.append((stem, match.group(0)))
    return hits


def _quote(terms) -> str:
    """Render cited terms as a readable quoted list."""
    quoted = ['"{0}"'.format(t) for t in terms]
    if len(quoted) == 1:
        return quoted[0]
    return ", ".join(quoted[:-1]) + " and " + quoted[-1]


def _integrity_failure(complaint_id: str, missing_field: str) -> Dict[str, str]:
    """Emit — never drop — a row that cannot be classified at all."""
    return {
        "complaint_id": complaint_id or "UNKNOWN_ID",
        "category": FALLBACK_CATEGORY,
        "priority": "Standard",
        "reason": (
            "Not classified because the {0} field is missing or blank, "
            "so there is no evidence to cite.".format(missing_field)
        ),
        "flag": REVIEW_FLAG,
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Never raises. Reads only `complaint_id` and `description` — `days_open`,
    `reported_by`, `ward` and `location` are intentionally ignored so that
    identical descriptions always classify identically.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Enforcement: data integrity. Emit, flag, never drop.
    if not complaint_id:
        return _integrity_failure(complaint_id, "complaint_id")
    if not description:
        return _integrity_failure(complaint_id, "description")

    strong, weak = _score_categories(description)
    severity_hits = _detect_severity(description)

    flag = ""

    if len(strong) == 1:
        # Exactly one complaint type named. Confident classification.
        category = list(strong.keys())[0]
        cited = strong[category] + weak.get(category, [])
        reason_core = "Classified as {0} on the strength of {1} in the description".format(
            category, _quote(cited)
        )
    elif len(strong) > 1:
        # Enforcement: ambiguity is detected, not resolved. Alphabetically first
        # tied category for determinism; both candidates named in the reason.
        contenders = sorted(strong.keys())
        category = contenders[0]
        all_cited = []
        for name in contenders:
            all_cited.extend(strong[name])
        reason_core = (
            "Ambiguous between {0} — the description contains {1}, so it is "
            "flagged for human review rather than forced into one category".format(
                " and ".join(contenders), _quote(all_cited)
            )
        )
        flag = REVIEW_FLAG
    elif len(weak) == 1:
        # Only corroborating evidence, no named type. Low-confidence guess, flagged.
        category = list(weak.keys())[0]
        reason_core = (
            "Only weak evidence {0} points to {1}, with no explicit complaint "
            "type named, so confidence is insufficient".format(
                _quote(weak[category]), category
            )
        )
        flag = REVIEW_FLAG
    else:
        # Enforcement: no evidence means refuse, never guess a plausible category.
        category = FALLBACK_CATEGORY
        snippet = " ".join(description.split()[:8])
        reason_core = (
            'No taxonomy keyword matched "{0}", so no category can be assigned '
            "from the description alone".format(snippet)
        )
        flag = REVIEW_FLAG

    # Enforcement: severity runs after the category and can only raise priority.
    if severity_hits:
        priority = "Urgent"
        stems = _quote([literal for _, literal in severity_hits])
        reason = "{0}; severity term {1} present so priority raised to Urgent.".format(
            reason_core, stems
        )
    else:
        priority = "Low" if category in LOW_PRIORITY_CATEGORIES else "Standard"
        reason = "{0}; no severity term present so priority is {1}.".format(
            reason_core, priority
        )

    # Final guard — a category outside the closed set can never leave here.
    if category not in ALLOWED_CATEGORIES:
        category = FALLBACK_CATEGORY
        flag = REVIEW_FLAG

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _report_blank_fields(rows: List[dict]) -> None:
    """Null report — printed before classification, per skills.md."""
    blanks = []
    for index, row in enumerate(rows, start=2):  # start=2 → CSV line number
        empty = sorted(k for k, v in row.items() if k and (v is None or str(v).strip() == ""))
        if empty:
            blanks.append((index, row.get("complaint_id") or "?", empty))

    if not blanks:
        print("Null report: no blank fields in any row.")
        return

    print("Null report: {0} row(s) contain blank fields".format(len(blanks)))
    for line_no, cid, empty in blanks:
        print("  line {0} ({1}): blank -> {2}".format(line_no, cid, ", ".join(empty)))


def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, classify each row, write results CSV.

    Guarantees: input row count == output row count; a row that raises is
    emitted as Other/NEEDS_REVIEW rather than aborting the batch; output is
    written even when some rows fail.
    """
    if not os.path.isfile(input_path):
        print("Error: input file not found: {0}".format(input_path), file=sys.stderr)
        sys.exit(1)

    try:
        with io.open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                print("Error: input CSV has no header row.", file=sys.stderr)
                sys.exit(1)
            missing = [c for c in ("complaint_id", "description") if c not in reader.fieldnames]
            if missing:
                print(
                    "Error: input CSV is missing required column(s): {0}".format(
                        ", ".join(missing)
                    ),
                    file=sys.stderr,
                )
                sys.exit(1)
            rows = list(reader)
    except (IOError, OSError, csv.Error, UnicodeDecodeError) as exc:
        print("Error: could not read {0}: {1}".format(input_path, exc), file=sys.stderr)
        sys.exit(1)

    _report_blank_fields(rows)

    results = []
    failed = 0
    for index, row in enumerate(rows, start=2):
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # one bad row must never abort the batch
            failed += 1
            results.append(
                {
                    "complaint_id": (row.get("complaint_id") or "UNKNOWN_ID").strip(),
                    "category": FALLBACK_CATEGORY,
                    "priority": "Standard",
                    "reason": "Classification failed on CSV line {0}: {1}.".format(index, exc),
                    "flag": REVIEW_FLAG,
                }
            )

    # Row-count invariant, asserted before we call the run clean.
    if len(results) != len(rows):
        print(
            "Error: row count mismatch — {0} in, {1} out.".format(len(rows), len(results)),
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with io.open(output_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
            writer.writeheader()
            writer.writerows(results)
    except (IOError, OSError) as exc:
        print("Error: could not write {0}: {1}".format(output_path, exc), file=sys.stderr)
        sys.exit(1)

    summary = {
        "total": len(results),
        "urgent": sum(1 for r in results if r["priority"] == "Urgent"),
        "standard": sum(1 for r in results if r["priority"] == "Standard"),
        "low": sum(1 for r in results if r["priority"] == "Low"),
        "needs_review": sum(1 for r in results if r["flag"] == REVIEW_FLAG),
        "failed": failed,
    }

    print(
        "\nTriage summary: {total} rows | Urgent {urgent} | Standard {standard} | "
        "Low {low} | {needs_review} flagged NEEDS_REVIEW | {failed} row error(s)".format(
            **summary
        )
    )
    counts = {}
    for result in results:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    print("Category spread: " + ", ".join(
        "{0}={1}".format(k, counts[k]) for k in sorted(counts)
    ))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
