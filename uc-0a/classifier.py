"""
UC-0A — Complaint Classifier

Implements the two skills in skills.md (classify_complaint, batch_classify)
under the enforcement rules in agents.md.

Design notes
- Deterministic and rule-based, standard library only (Python 3.9+).
- Only the complaint description is used as evidence (never ward or location).
- Category is always one of the 10 allowed strings.
- Priority is Urgent whenever a severity keyword matches (case-insensitive, stem match).
- Every row gets a one-sentence reason quoting words from the description.
- NEEDS_REVIEW is set when evidence is weak, tied, or absent. Nothing is guessed silently.
- A bad row never stops the batch.
"""
import argparse
import csv
import re
import sys
from typing import Dict, List, Tuple

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]
NEEDS_REVIEW = "NEEDS_REVIEW"

# Severity keywords from the UC-0A README. Stem match, case-insensitive:
# "injured", "children", "hospitalised", "collapsed" all trigger.
SEVERITY_PATTERNS = [
    ("injury", r"\binjur\w*"),
    ("child", r"\bchild\w*"),
    ("school", r"\bschool\w*"),
    ("hospital", r"\bhospital\w*"),
    ("ambulance", r"\bambulance\w*"),
    ("fire", r"\bfire\w*"),
    ("hazard", r"\bhazard\w*"),
    ("fell", r"\bfell\b"),
    ("collapse", r"\bcollapse\w*"),
]
_SEVERITY = [(name, re.compile(p, re.IGNORECASE)) for name, p in SEVERITY_PATTERNS]

# Low priority is reserved for minor or cosmetic complaints with no severity keyword.
LOW_MARKERS = re.compile(r"\b(cosmetic|minor|faded|graffiti|peeling paint)\b", re.IGNORECASE)

# (category, regex, weight). Weight 2 = strong evidence, 1 = weak, 0.5 = context only.
# Each rule counts at most once per description.
_RULE_DEFS = [
    ("Pothole", r"pot\s?holes?", 2),

    ("Flooding", r"flood\w*", 2),
    ("Flooding", r"waterlog\w*|standing in water", 2),
    ("Flooding", r"\brain(?:water|fall)?\b", 0.5),

    ("Streetlight", r"street\s?lights?|street\s?lamps?", 2),
    ("Streetlight", r"\blights?\s+(?:are\s+)?out\b", 2),
    ("Streetlight", r"\bunlit\b|no lighting", 2),
    ("Streetlight", r"\bdark(?:ness)?\b", 1),

    ("Waste", r"garbage|\bwaste\b|litter|dumped|dumping|\bbins?\b|rubbish", 2),
    ("Waste", r"dead animal", 1),

    ("Noise", r"music|\bnoise\b|noisy|\bloud\b|amplifiers?|drilling|audible|band playing|honking|siren", 2),
    ("Noise", r"\bidling\b", 1),

    ("Road Damage", r"road surface", 2),
    ("Road Damage", r"\bcrack\w*", 2),
    ("Road Damage", r"sinking|\bsunk\b|subsid\w*", 2),
    ("Road Damage", r"\bbuckl\w*", 2),
    ("Road Damage", r"\bcrater\b", 2),
    ("Road Damage", r"footpath|pavement|sidewalk", 2),
    ("Road Damage", r"\bcollapse\w*", 2),
    ("Road Damage", r"\bpaving\b", 1),
    ("Road Damage", r"\bmanhole", 1),

    ("Heat Hazard", r"\d+\s*°\s*c\b", 2),
    ("Heat Hazard", r"temperatures?", 2),
    ("Heat Hazard", r"\bmelting\b|\bbubbling\b|\bburns?\b", 2),
    ("Heat Hazard", r"\bheat\b", 1),
    ("Heat Hazard", r"full sun", 1),

    ("Drain Blockage", r"drain\w*[^.]{0,40}block\w*|block\w*[^.]{0,40}drain\w*", 2),
    ("Drain Blockage", r"\bmanhole", 1),
]
_RULES = [(c, re.compile(p, re.IGNORECASE), w) for c, p, w in _RULE_DEFS]

# "at flooding risk" describes a possible future event, not a flood, so it is ignored.
_FLOOD_RISK = re.compile(r"(?:at\s+)?flood(?:ing)?\s+risk", re.IGNORECASE)

# Heritage Damage needs a heritage context word AND a damage word in the description.
_HERITAGE_CONTEXT = re.compile(r"heritage|historic\w*|ancient|tagore|museum|marble palace", re.IGNORECASE)
_HERITAGE_DAMAGE = re.compile(
    r"defac\w*|knocked|broken|removed|not\s+(?:been\s+)?(?:replaced|restored)"
    r"|cobblestones?|subsid\w*|\bcrack\w*|damag\w*|vandal\w*|demolish\w*",
    re.IGNORECASE,
)


def _clean(value) -> str:
    """Return a stripped string; None and non-strings become ''."""
    if value is None:
        return ""
    return str(value).strip()


def _quote_list(words: List[str]) -> str:
    seen = []  # type: List[str]
    for w in words:
        w = re.sub(r"\s+", " ", w.strip())
        if w and w.lower() not in [s.lower() for s in seen]:
            seen.append(w)
    return ", ".join('"%s"' % w.replace('"', "'") for w in seen[:3])


def _score(description: str) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    text = _FLOOD_RISK.sub(" ", description)
    scores = {c: 0.0 for c in CATEGORIES}
    evidence = {c: [] for c in CATEGORIES}  # type: Dict[str, List[str]]
    for category, pattern, weight in _RULES:
        m = pattern.search(text)
        if m:
            scores[category] += weight
            evidence[category].append(m.group(0))
    ctx = _HERITAGE_CONTEXT.search(text)
    if ctx:
        scores["Heritage Damage"] += 0.5
        evidence["Heritage Damage"].append(ctx.group(0))
        dmg = _HERITAGE_DAMAGE.search(text)
        if dmg:
            scores["Heritage Damage"] += 2
            evidence["Heritage Damage"].append(dmg.group(0))
    return scores, evidence


def _severity_hits(description: str) -> List[str]:
    hits = []
    for _name, pattern in _SEVERITY:
        m = pattern.search(description)
        if m:
            hits.append(m.group(0))
    return hits


def _fallback(complaint_id: str, reason: str) -> Dict[str, str]:
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
    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    Never raises: any problem yields category Other + NEEDS_REVIEW.
    """
    complaint_id = ""
    try:
        if not isinstance(row, dict):
            return _fallback("", "The row was not readable, so it could not be classified.")
        complaint_id = _clean(row.get("complaint_id"))
        description = _clean(row.get("description"))

        if not description:
            return _fallback(
                complaint_id,
                "The description is empty or missing, so it could not be classified.",
            )

        severity = _severity_hits(description)
        scores, evidence = _score(description)
        order = {c: i for i, c in enumerate(CATEGORIES)}
        ranked = sorted(CATEGORIES, key=lambda c: (-scores[c], order[c]))
        top, runner_up = ranked[0], ranked[1]
        top_score, second_score = scores[top], scores[runner_up]

        if top_score <= 0:
            category, flag, why_flag = "Other", NEEDS_REVIEW, "no defined category matches"
        else:
            category = top
            flag, why_flag = "", ""
            if top_score < 2:
                flag, why_flag = NEEDS_REVIEW, "the evidence is weak"
            elif second_score >= 1 and top_score - second_score < 2:
                flag = NEEDS_REVIEW
                why_flag = "it also fits %s" % runner_up

        if not complaint_id:
            flag = NEEDS_REVIEW
            why_flag = (why_flag + " and " if why_flag else "") + "the complaint_id is missing"

        priority = "Urgent" if severity else ("Low" if LOW_MARKERS.search(description) else "Standard")

        if category == "Other" and top_score <= 0:
            snippet = re.sub(r"\s+", " ", description)
            if len(snippet) > 60:
                snippet = snippet[:60].rsplit(" ", 1)[0] + " ..."
            snippet = snippet.replace('"', "'").replace(". ", ", ").rstrip(" .")
            reason = 'No defined category matches the description ("%s")' % snippet
        else:
            reason = "Classified %s because the description mentions %s" % (
                category, _quote_list(evidence[category]))
        if why_flag and not reason.endswith(why_flag):
            reason += ", flagged for review because %s" % why_flag if top_score > 0 else \
                ", so it is flagged for review"
        if severity:
            reason += ", and priority is Urgent because it mentions %s" % _quote_list(severity)
        reason += "."

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except Exception as exc:  # noqa: BLE001 - a bad row must never stop the batch
        return _fallback(complaint_id, "Classification failed (%s), so it needs manual review." % type(exc).__name__)


def batch_classify(input_path: str, output_path: str):
    """
    Read the input CSV, classify each row, write the results CSV.
    Flags nulls, does not crash on bad rows, and writes output even if some rows fail.
    Raises ValueError (and writes nothing) if the input is missing or has no description column.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            if "description" not in fields:
                raise ValueError("Input CSV has no 'description' column: %s" % input_path)
            rows = list(reader)
    except FileNotFoundError:
        raise ValueError("Input file not found: %s" % input_path)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # noqa: BLE001 - defensive; classify_complaint should not raise
            results.append(_fallback(_clean(row.get("complaint_id")) if isinstance(row, dict) else "",
                                     "Classification failed (%s), so it needs manual review." % type(exc).__name__))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r["flag"] == NEEDS_REVIEW)
    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    print("Rows read: %d | rows written: %d | Urgent: %d | NEEDS_REVIEW: %d"
          % (len(rows), len(results), urgent, flagged))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except ValueError as err:
        print("Error: %s" % err, file=sys.stderr)
        sys.exit(1)
    print("Done. Results written to %s" % args.output)
