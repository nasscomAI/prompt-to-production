"""
UC-0A — Complaint Classifier

Deterministic, rule-based implementation of the contract in agents.md / skills.md.
Classification reads the `description` field only: ward, location, reported_by and
days_open are deliberately ignored so that reporter identity or backlog age can
never change a priority.
"""
import argparse
import csv
import os
import re
import sys

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Tie-break order only. It picks a category string when two categories tie;
# it never suppresses the NEEDS_REVIEW flag on that tie.
PRECEDENCE = [
    "Pothole", "Drain Blockage", "Flooding", "Streetlight", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Waste", "Noise", "Other",
]

STRONG, WEAK = 2, 1

# (regex, weight) per category. Strong = names the problem, weak = circumstantial.
CATEGORY_KEYWORDS = {
    "Pothole": [
        (r"\bpot[\s-]?holes?\b", STRONG),
        (r"\bcraters?\b", WEAK),
    ],
    "Flooding": [
        (r"\bflood(?:s|ed|ing)?\b", STRONG),
        (r"\bwater[\s-]?logg(?:ed|ing)\b", STRONG),
        (r"\binundated\b", STRONG),
        (r"\bstanding water\b", WEAK),
        (r"\bknee[\s-]deep\b", WEAK),
    ],
    "Streetlight": [
        (r"\bstreet[\s-]?lights?\b", STRONG),
        (r"\bstreet[\s-]?lamps?\b", STRONG),
        (r"\blamp[\s-]?posts?\b", STRONG),
        (r"\blights? (?:are )?out\b", STRONG),
        (r"\bno lighting\b", STRONG),
        (r"\bdark at night\b", WEAK),
        (r"\bunlit\b", WEAK),
    ],
    "Waste": [
        (r"\bgarbage\b", STRONG),
        (r"\bwaste\b", STRONG),
        (r"\btrash\b", STRONG),
        (r"\brubbish\b", STRONG),
        (r"\blitter(?:ing|ed)?\b", STRONG),
        (r"\bdead animals?\b", STRONG),
        (r"\bdumped?\b", STRONG),
        (r"\bbins?\b", WEAK),
        (r"\bsmell\b", WEAK),
    ],
    "Noise": [
        (r"\bnoise\b", STRONG),
        (r"\bloud\b", STRONG),
        (r"\bmusic\b", STRONG),
        (r"\bloudspeakers?\b", STRONG),
        (r"\bdj\b", STRONG),
        (r"\bhorns?\b", WEAK),
    ],
    "Road Damage": [
        (r"\broad (?:surface|damage)\b", STRONG),
        (r"\bdamaged road\b", STRONG),
        (r"\bcrack(?:s|ed|ing)?\b", STRONG),
        (r"\bsinking\b", STRONG),
        (r"\bsunken\b", STRONG),
        (r"\bcaved[\s-]?in\b", STRONG),
        (r"\bfoot[\s-]?paths?\b", STRONG),
        (r"\bpavements?\b", STRONG),
        (r"\buneven\b", WEAK),
    ],
    "Heritage Damage": [
        (r"\bheritage\b", STRONG),
        (r"\bmonuments?\b", STRONG),
        (r"\bhistoric(?:al)?\b", STRONG),
        (r"\bwada\b", WEAK),
    ],
    "Heat Hazard": [
        (r"\bheat[\s-]?wave\b", STRONG),
        (r"\bheat[\s-]?stroke\b", STRONG),
        (r"\bsun[\s-]?stroke\b", STRONG),
        (r"\bextreme heat\b", STRONG),
        (r"\bno shade\b", WEAK),
    ],
    "Drain Blockage": [
        (r"\bdrains? (?:is |are )?(?:blocked|clogged|choked|overflowing)\b", STRONG),
        (r"\b(?:blocked|clogged|choked) drains?\b", STRONG),
        (r"\bdrainage (?:blocked|clogged|choked)\b", STRONG),
        (r"\bsewer(?:age|s)?\b", STRONG),
        (r"\bman[\s-]?holes?\b", WEAK),
        (r"\bgutters?\b", WEAK),
        (r"\bdrains?\b", WEAK),
    ],
}

# Exact keyword list from the UC-0A schema, with plain inflections.
SEVERITY_KEYWORDS = {
    "injury": r"\binjur(?:y|ies|ed)\b",
    "child": r"\bchild(?:ren)?\b",
    "school": r"\bschools?\b",
    "hospital": r"\bhospitals?\b",
    "ambulance": r"\bambulances?\b",
    "fire": r"\bfires?\b",
    "hazard": r"\bhazard(?:s|ous)?\b",
    "fell": r"\bfell\b",
    "collapse": r"\bcollaps(?:e|ed|es|ing)\b",
}

# Categories that are nuisance-grade when nothing severe is said.
LOW_DEFAULT_CATEGORIES = {"Waste", "Noise", "Other"}

NEEDS_REVIEW = "NEEDS_REVIEW"


def _quote(terms):
    return ", ".join("'{}'".format(t) for t in terms)


def _match_severity(text):
    """Returns the literal matched substrings for every severity keyword present."""
    hits = []
    for pattern in SEVERITY_KEYWORDS.values():
        found = re.search(pattern, text, re.IGNORECASE)
        if found:
            hits.append(found.group(0).lower())
    return hits


def _score_categories(text):
    """Returns {category: (total_weight, [matched terms], has_strong_hit)}."""
    scores = {}
    for category, patterns in CATEGORY_KEYWORDS.items():
        weight, terms, strong, spans = 0, [], False, []
        for pattern, pattern_weight in sorted(patterns, key=lambda p: -p[1]):
            found = re.search(pattern, text, re.IGNORECASE)
            if not found:
                continue
            # 'drain' inside 'drain blocked' is the same evidence, not a second hit.
            if any(s <= found.start() and found.end() <= e for s, e in spans):
                continue
            spans.append(found.span())
            weight += pattern_weight
            terms.append(found.group(0).lower())
            strong = strong or pattern_weight == STRONG
        if weight:
            scores[category] = (weight, terms, strong)
    return scores


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    row = row or {}
    complaint_id = (row.get("complaint_id") or "").strip()
    description = row.get("description")
    description = description.strip() if isinstance(description, str) else ""

    id_problem = not complaint_id
    if id_problem:
        complaint_id = "UNKNOWN"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty, so no category or severity "
                      "evidence exists and the row cannot be classified.",
            "flag": NEEDS_REVIEW,
        }

    severity_hits = _match_severity(description)
    scores = _score_categories(description)

    flag = ""
    rival = None

    if not scores:
        category, terms = "Other", []
        flag = NEEDS_REVIEW
    else:
        ranked = sorted(
            scores.items(),
            key=lambda item: (-item[1][0], PRECEDENCE.index(item[0])),
        )
        category, (top_weight, terms, has_strong) = ranked[0]

        if len(ranked) > 1 and ranked[1][1][0] == top_weight:
            flag = NEEDS_REVIEW
            rival = ranked[1][0]
        elif not has_strong:
            flag = NEEDS_REVIEW

    if severity_hits:
        priority = "Urgent"
    elif category in LOW_DEFAULT_CATEGORIES:
        priority = "Low"
    else:
        priority = "Standard"

    if terms:
        reason = "Category {} from matched term(s) {} in the description".format(
            category, _quote(terms))
    else:
        reason = "No category keyword matched the description, so category Other"

    if rival:
        reason += "; {} matched with equal weight, so the row is flagged".format(rival)
    elif flag and terms:
        reason += ", which is weak evidence only, so the row is flagged"
    elif flag:
        reason += " and the row is flagged"

    if severity_hits:
        reason += "; priority Urgent because severity keyword(s) {} appear".format(
            _quote(severity_hits))
    else:
        reason += "; priority {} because no severity keyword appears".format(priority)

    if id_problem:
        reason += "; complaint_id was missing in the source row"
        flag = NEEDS_REVIEW

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason + ".",
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, classify each row, write results CSV.
    One output row per input row, in input order. A bad row never aborts the batch.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "description" not in reader.fieldnames:
                raise ValueError(
                    "input CSV has no 'description' column (found: {})".format(
                        reader.fieldnames))
            rows = list(reader)
    except (OSError, ValueError) as error:
        print("ERROR: cannot read {}: {}".format(input_path, error), file=sys.stderr)
        sys.exit(1)

    results, failed = [], 0
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as error:  # a single unexpected row must not kill the file
            failed += 1
            results.append({
                "complaint_id": (row.get("complaint_id") or "UNKNOWN").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": "Row could not be classified ({}: {}).".format(
                    type(error).__name__, error),
                "flag": NEEDS_REVIEW,
            })

    parent = os.path.dirname(os.path.abspath(output_path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    ids = [r["complaint_id"] for r in results]
    summary = {
        "total": len(results),
        "urgent": sum(1 for r in results if r["priority"] == "Urgent"),
        "standard": sum(1 for r in results if r["priority"] == "Standard"),
        "low": sum(1 for r in results if r["priority"] == "Low"),
        "needs_review": sum(1 for r in results if r["flag"] == NEEDS_REVIEW),
        "failed": failed,
        "duplicate_ids": len(ids) - len(set(ids)),
    }
    print(summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
