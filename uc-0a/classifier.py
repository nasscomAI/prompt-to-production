"""
UC-0A - Complaint Classifier

Implements the enforcement rules declared in uc-0a/agents.md:

  TAXONOMY LOCK        category is validated against a fixed 10-value enum before write
  SEVERITY OVERRIDE    severity keywords force priority = Urgent, after category is set
  LOW IS A RULE        Low requires an explicit, testable condition - never a vibe
  JUSTIFICATION        every row carries a reason quoting terms from its own description
  REFUSAL ON AMBIGUITY weak or contested evidence produces NEEDS_REVIEW, not confidence
  FAIL SOFT            malformed rows are emitted, not dropped; row count in == row count out

Standard library only. Deterministic: the same input file always produces the same
output file, which is what makes the verification checks in agents.md meaningful.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv \
                         --output results_pune.csv
"""

import argparse
import csv
import re
import sys
from typing import Dict, List, Tuple

# --------------------------------------------------------------------------
# Schema - the only values this classifier is allowed to emit.
# Order is significant: it is the deterministic tie-breaker for equal scores.
# --------------------------------------------------------------------------

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

OUTPUT_COLUMNS = ["complaint_id", "category", "priority", "reason", "flag"]

NEEDS_REVIEW = "NEEDS_REVIEW"

# --------------------------------------------------------------------------
# Enforcement thresholds - named, so a reviewer can argue with the numbers.
# --------------------------------------------------------------------------

MIN_CONFIDENT_SCORE = 2.0   # below this, the evidence is a single weak term
AMBIGUITY_MARGIN = 1.5      # top two categories this close means "it is both"

# --------------------------------------------------------------------------
# SEVERITY OVERRIDE
# The nine keywords from the UC-0A schema, written as whole-word patterns with
# their common inflections. Word boundaries matter: 'fell' must not fire on
# 'fellow', while 'child' must fire on 'children'.
# --------------------------------------------------------------------------

SEVERITY_PATTERNS = [
    re.compile(r"\binjur(?:y|ies|ed|ing)\b", re.I),
    re.compile(r"\bchild(?:ren|'s|s)?\b", re.I),
    re.compile(r"\bschools?\b", re.I),
    re.compile(r"\bhospital(?:s|ised|ized)?\b", re.I),
    re.compile(r"\bambulances?\b", re.I),
    re.compile(r"\bfires?\b", re.I),
    re.compile(r"\bhazard(?:s|ous)?\b", re.I),
    re.compile(r"\bfell\b", re.I),
    re.compile(r"\bcollaps(?:e|ed|es|ing)\b", re.I),
]

# --------------------------------------------------------------------------
# LOW IS A RULE
# Low priority is available only to these categories, and only when the
# description carries none of the impact terms below.
# --------------------------------------------------------------------------

LOW_ELIGIBLE_CATEGORIES = {"Noise", "Heritage Damage"}

IMPACT_PATTERN = re.compile(
    r"\b(?:safety|unsafe|risk|danger(?:ous)?|health|structural|blocked|emergency|accident)\b",
    re.I,
)

# --------------------------------------------------------------------------
# Category evidence patterns: (regex, weight).
# Weight 3 = the term names the category outright.
# Weight 2 = a strong, near-unambiguous symptom.
# Weight 1 = a supporting hint that cannot carry a row on its own.
# --------------------------------------------------------------------------

CATEGORY_PATTERNS: Dict[str, List[Tuple["re.Pattern", float]]] = {
    "Pothole": [
        (re.compile(r"\bpot[\s-]?holes?\b", re.I), 3.0),
    ],
    "Flooding": [
        (re.compile(r"\bflood(?:s|ed|ing)?\b", re.I), 3.0),
        (re.compile(r"\bwater[\s-]?logg(?:ed|ing)\b", re.I), 3.0),
        (re.compile(r"\bknee[\s-]deep\b", re.I), 2.0),
        (re.compile(r"\bstanding in water\b", re.I), 2.0),
        (re.compile(r"\brain[\s-]?water\b", re.I), 1.0),
    ],
    "Streetlight": [
        (re.compile(r"\bstreet[\s-]?lights?\b", re.I), 3.0),
        (re.compile(r"\blamp[\s-]?posts?\b", re.I), 2.0),
        (re.compile(r"\bunlit\b", re.I), 2.0),
        (re.compile(r"\blights? out\b", re.I), 2.0),
        (re.compile(r"\blighting\b", re.I), 2.0),
        (re.compile(r"\bdark(?:ness)?\b", re.I), 1.0),
        (re.compile(r"\bsubstation\b", re.I), 1.0),
    ],
    "Waste": [
        (re.compile(r"\bwaste\b", re.I), 3.0),
        (re.compile(r"\bgarbage\b", re.I), 3.0),
        (re.compile(r"\brubbish\b", re.I), 3.0),
        (re.compile(r"\blitter(?:ing)?\b", re.I), 2.0),
        (re.compile(r"\bbins?\b", re.I), 2.0),
        (re.compile(r"\bdumped\b", re.I), 2.0),
        (re.compile(r"\bdead animal\b", re.I), 2.0),
    ],
    "Noise": [
        (re.compile(r"\bnoise\b", re.I), 3.0),
        (re.compile(r"\bmusic\b", re.I), 3.0),
        (re.compile(r"\bamplifiers?\b", re.I), 3.0),
        (re.compile(r"\bdecibels?\b", re.I), 3.0),
        (re.compile(r"\bloud\b", re.I), 2.0),
        (re.compile(r"\bdrilling\b", re.I), 2.0),
        (re.compile(r"\bidling\b", re.I), 2.0),
        (re.compile(r"\bband playing\b", re.I), 2.0),
    ],
    "Road Damage": [
        (re.compile(r"\broad (?:surface |)collaps(?:e|ed)\b", re.I), 3.0),
        (re.compile(r"\bsubsid(?:ed|ence|ing)\b", re.I), 2.0),
        (re.compile(r"\bcraters?\b", re.I), 2.0),
        (re.compile(r"\bbuckled\b", re.I), 2.0),
        (re.compile(r"\bcracked\b", re.I), 2.0),
        (re.compile(r"\bsinking\b", re.I), 2.0),
        (re.compile(r"\broad surface\b", re.I), 2.0),
        (re.compile(r"\bfoot[\s-]?path\b", re.I), 2.0),
        (re.compile(r"\bmanhole\b", re.I), 2.0),
        (re.compile(r"\bpaving\b", re.I), 1.0),
        (re.compile(r"\btarmac\b", re.I), 1.0),
        (re.compile(r"\bcobblestones?\b", re.I), 1.0),
    ],
    "Heritage Damage": [
        (re.compile(r"\bheritage\b", re.I), 3.0),
        (re.compile(r"\bhistoric(?:al)?\b", re.I), 3.0),
        (re.compile(r"\bmonuments?\b", re.I), 2.0),
        (re.compile(r"\bancient\b", re.I), 2.0),
        (re.compile(r"\bold city\b", re.I), 1.0),
        (re.compile(r"\bmuseum\b", re.I), 1.0),
    ],
    "Heat Hazard": [
        (re.compile(r"\bheat[\s-]?waves?\b", re.I), 3.0),
        (re.compile(r"\bheat\b", re.I), 3.0),
        (re.compile(r"\bmelting\b", re.I), 3.0),
        (re.compile(r"\btemperatures?\b", re.I), 2.0),
        (re.compile(r"\d+\s*(?:°|deg(?:rees)?)\s*c\b", re.I), 2.0),
        (re.compile(r"\bburns?\b", re.I), 2.0),
        (re.compile(r"\bsun\b", re.I), 1.0),
    ],
    "Drain Blockage": [
        (re.compile(r"\bstorm[\s-]?water\b", re.I), 2.0),
        (re.compile(r"\bdrain(?:s|age|ing|ed)?\b", re.I), 2.0),
        (re.compile(r"\bsewer(?:s|age)?\b", re.I), 2.0),
        (re.compile(r"\bblock(?:ed|age|ing)\b", re.I), 1.0),
    ],
    # "Other" is never scored - it is the explicit refusal outcome.
}


# --------------------------------------------------------------------------
# Skill: detect_severity
# --------------------------------------------------------------------------

def detect_severity(description: str) -> List[str]:
    """Return the literal severity terms present in the description.

    This is the single authority for escalating to Urgent. It reads the
    description and nothing else - never the ward, the age of the complaint,
    or who reported it.
    """
    if not isinstance(description, str) or not description.strip():
        return []

    found = []
    for pattern in SEVERITY_PATTERNS:
        match = pattern.search(description)
        if match:
            term = match.group(0)
            if term.lower() not in {t.lower() for t in found}:
                found.append(term)
    return found


# --------------------------------------------------------------------------
# Skill: score_categories
# --------------------------------------------------------------------------

def score_categories(description: str) -> List[Tuple[str, float, List[str]]]:
    """Score the description against every allowed category.

    Returns (category, score, matched_terms) sorted by score descending, with
    ties broken by the fixed schema order so runs are reproducible. A pattern
    contributes its weight once, however many times it occurs - repetition is
    not extra evidence.
    """
    if not isinstance(description, str) or not description.strip():
        return []

    scored = []
    for index, category in enumerate(ALLOWED_CATEGORIES):
        patterns = CATEGORY_PATTERNS.get(category)
        if not patterns:
            continue

        score = 0.0
        matched_terms: List[str] = []
        for pattern, weight in patterns:
            match = pattern.search(description)
            if match:
                score += weight
                term = match.group(0).strip()
                if term.lower() not in {t.lower() for t in matched_terms}:
                    matched_terms.append(term)

        if score > 0:
            scored.append((category, score, matched_terms, index))

    scored.sort(key=lambda item: (-item[1], item[3]))
    return [(cat, score, terms) for cat, score, terms, _ in scored]


# --------------------------------------------------------------------------
# Priority resolution
# --------------------------------------------------------------------------

def _resolve_priority(description: str, category: str, severity_terms: List[str]) -> str:
    """SEVERITY OVERRIDE first, then the Low rule, then Standard as the default."""
    if severity_terms:
        return "Urgent"

    if (
        category in LOW_ELIGIBLE_CATEGORIES
        and not IMPACT_PATTERN.search(description or "")
    ):
        return "Low"

    return "Standard"


def _quote(terms: List[str]) -> str:
    return ", ".join("'{}'".format(t) for t in terms)


# --------------------------------------------------------------------------
# Skill: classify_complaint
# --------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns a dict with exactly: complaint_id, category, priority, reason, flag.
    No extra fields are ever added, and no field is ever left blank except
    `flag`, whose empty value means "no review needed".
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = row.get("description")
    description = description.strip() if isinstance(description, str) else ""

    # FAIL SOFT: a row with no description is still a row.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty; no evidence available to classify.",
            "flag": NEEDS_REVIEW,
        }

    severity_terms = detect_severity(description)
    ranked = score_categories(description)

    # REFUSAL ON AMBIGUITY (a): nothing matched at all.
    if not ranked:
        priority = _resolve_priority(description, "Other", severity_terms)
        reason = "No allowed-category term found in description; left as Other rather than guessed"
        if severity_terms:
            reason += "; priority Urgent from severity term {}".format(_quote(severity_terms))
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason + ".",
            "flag": NEEDS_REVIEW,
        }

    top_category, top_score, top_terms = ranked[0]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0.0

    flag = ""
    ambiguity_note = ""

    # REFUSAL ON AMBIGUITY (b): the win rests on one weak term.
    if top_score < MIN_CONFIDENT_SCORE:
        flag = NEEDS_REVIEW
        ambiguity_note = "; evidence is a single weak term, so flagged for review"

    # REFUSAL ON AMBIGUITY (c): two categories are genuinely both supported.
    elif runner_up_score > 0 and (top_score - runner_up_score) < AMBIGUITY_MARGIN:
        flag = NEEDS_REVIEW
        ambiguity_note = "; {} is equally supported by {}, so flagged for review".format(
            ranked[1][0], _quote(ranked[1][2])
        )

    priority = _resolve_priority(description, top_category, severity_terms)

    # JUSTIFICATION IS EVIDENCE: quote the terms actually found in this row.
    reason = "Category {} from matched term {}".format(top_category, _quote(top_terms))
    if severity_terms:
        reason += "; priority Urgent from severity term {}".format(_quote(severity_terms))
    elif priority == "Low":
        reason += "; priority Low as no severity or impact term is present"
    else:
        reason += "; priority Standard as no severity term is present"
    reason += ambiguity_note + "."

    return {
        "complaint_id": complaint_id,
        "category": top_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# --------------------------------------------------------------------------
# TAXONOMY LOCK - last gate before anything is written.
# --------------------------------------------------------------------------

def _validate_row(result: dict, position: int) -> dict:
    """Coerce any out-of-schema result into Other / NEEDS_REVIEW.

    This is belt-and-braces: classify_complaint should never produce an invalid
    value, but the enum is the contract and the contract is checked at the edge.
    """
    if not result.get("complaint_id"):
        result["complaint_id"] = "ROW_{}".format(position)

    if result.get("category") not in ALLOWED_CATEGORIES:
        result["reason"] = "Rejected out-of-schema category {!r}; forced to Other.".format(
            result.get("category")
        )
        result["category"] = "Other"
        result["flag"] = NEEDS_REVIEW

    if result.get("priority") not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"
        result["flag"] = NEEDS_REVIEW

    if result.get("flag") not in (NEEDS_REVIEW, ""):
        result["flag"] = NEEDS_REVIEW

    if not (result.get("reason") or "").strip():
        result["reason"] = "No justification produced; flagged for review."
        result["flag"] = NEEDS_REVIEW

    return {key: result.get(key, "") for key in OUTPUT_COLUMNS}


# --------------------------------------------------------------------------
# Skill: batch_classify
# --------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> int:
    """Read the city CSV, classify every row in order, write the results CSV.

    Returns the number of rows written. Row count out always equals row count in.
    """
    try:
        # utf-8-sig strips the BOM some spreadsheet exports prepend.
        with open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except FileNotFoundError:
        sys.stderr.write("ERROR: input file not found: {}\n".format(input_path))
        sys.exit(1)
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write("ERROR: could not read {}: {}\n".format(input_path, exc))
        sys.exit(1)

    if not rows:
        sys.stderr.write("ERROR: {} contains no data rows.\n".format(input_path))
        sys.exit(1)

    if "description" not in rows[0]:
        sys.stderr.write(
            "ERROR: {} has no 'description' column; found: {}\n".format(
                input_path, ", ".join(rows[0].keys())
            )
        )
        sys.exit(1)

    # FAIL SOFT, NEVER SILENT - data quality is reported before results are trusted.
    missing_desc = [
        i + 1 for i, r in enumerate(rows)
        if not (r.get("description") or "").strip()
    ]
    missing_id = [
        i + 1 for i, r in enumerate(rows)
        if not (r.get("complaint_id") or "").strip()
    ]
    sys.stderr.write("Null report for {}\n".format(input_path))
    sys.stderr.write("  rows read:                 {}\n".format(len(rows)))
    sys.stderr.write("  rows missing description:  {} {}\n".format(
        len(missing_desc), missing_desc or ""))
    sys.stderr.write("  rows missing complaint_id: {} {}\n".format(
        len(missing_id), missing_id or ""))

    results = []
    for position, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
        except Exception as exc:  # one bad row must not cost the other fourteen
            result = {
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": "Row {} raised {}: {}; emitted for manual review.".format(
                    position, type(exc).__name__, exc
                ),
                "flag": NEEDS_REVIEW,
            }
        results.append(_validate_row(result, position))

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(results)
    except OSError as exc:
        sys.stderr.write("ERROR: could not write {}: {}\n".format(output_path, exc))
        sys.exit(1)

    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    standard = sum(1 for r in results if r["priority"] == "Standard")
    low = sum(1 for r in results if r["priority"] == "Low")
    review = sum(1 for r in results if r["flag"] == NEEDS_REVIEW)

    sys.stderr.write("Summary\n")
    sys.stderr.write("  rows written: {} (in: {})\n".format(len(results), len(rows)))
    sys.stderr.write("  Urgent: {}  Standard: {}  Low: {}\n".format(urgent, standard, low))
    sys.stderr.write("  NEEDS_REVIEW: {}\n".format(review))

    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to {}".format(args.output))