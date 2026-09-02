"""
UC-0A — Complaint Classifier

Implements the five enforcement rules in agents.md and the two skills declared
in skills.md. Every rule is checked in code rather than assumed: the permitted
category set is validated against the value actually emitted, severity terms are
matched by stem, and ambiguity is reported instead of resolved.
"""
import argparse
import csv
import re

# Rule 1 — the permitted set. Validated against every emitted value below.
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Rule 2 — the nine README severity terms, each as a stem family. The data writes
# several of them inflected, and both naive approaches miss rows: a substring
# test fails on "injury" in "injured", a whole-word test fails on "child" in
# "children". `fell` covers the past forms, an incident that already happened.
SEVERITY_PATTERNS = {
    "injury":    r"\binjur(?:y|ies|ed|ing)\b",
    "child":     r"\bchild(?:ren|s)?\b",
    "school":    r"\bschool(?:s|children)?\b",
    "hospital":  r"\bhospital(?:s|ised|ized|isation|ization)?\b",
    "ambulance": r"\bambulance(?:s)?\b",
    "fire":      r"\bfire(?:s)?\b",
    "hazard":    r"\bhazard(?:s|ous)?\b",
    "fell":      r"\b(?:fell|fallen)\b",
    "collapse":  r"\bcollaps(?:e|ed|es|ing)\b",
}

# Rule 4 — cues are weighted and scored rather than matched first-wins, so a
# description naming two things surfaces as a tie instead of silently taking
# whichever branch is written first. PRIMARY names the thing complained about
# (weight 2); SECONDARY is corroborating detail (weight 1).
CATEGORY_CUES = {
    "Pothole": {
        "primary":   [r"\bpothole(?:s)?\b"],
        "secondary": [r"\btyre (?:damage|blowouts?)\b"],
    },
    "Flooding": {
        "primary":   [r"\bflood(?:s|ed|ing)?\b", r"\bwaterlogg(?:ed|ing)\b",
                      r"\bknee-deep\b", r"\bstanding in water\b"],
        "secondary": [r"\brainwater\b", r"\bstranded\b"],
    },
    "Streetlight": {
        "primary":   [r"\bstreet ?light(?:s)?\b", r"\bunlit\b", r"\blamp post\b",
                      r"\blights? out\b", r"\bsubstation\b"],
        "secondary": [r"\bdark(?:ness)?\b", r"\bwiring theft\b"],
    },
    "Waste": {
        "primary":   [r"\bwaste\b", r"\bgarbage\b", r"\brubbish\b", r"\bbins?\b",
                      r"\bdead animal\b", r"\blitter\b"],
        "secondary": [r"\bdumped\b", r"\boverflow(?:ing)?\b"],
    },
    "Noise": {
        "primary":   [r"\bnoise\b", r"\bmusic\b", r"\bamplifiers?\b",
                      r"\bdrilling\b", r"\bband\b", r"\bidling\b"],
        "secondary": [r"\baudible\b", r"\bpast midnight\b", r"\b\d+ ?[ap]m\b"],
    },
    "Road Damage": {
        "primary":   [r"\bsubsid(?:ed|ence|ing)\b", r"\bbuckled\b", r"\bcrater\b",
                      r"\bcracked\b", r"\bcobblestones?\b", r"\bmanhole\b",
                      r"\bcollaps(?:e|ed)\b", r"\bfootpath\b"],
        "secondary": [r"\bpaving\b", r"\broad surface\b", r"\btiles broken\b"],
    },
    "Heat Hazard": {
        "primary":   [r"\bheat(?:wave)?\b", r"\bmelting\b", r"\bbubbling\b",
                      r"\bburns?\b", r"\b\d+\s*°?\s*c\b"],
        "secondary": [r"\btemperature(?:s)?\b", r"\bfull sun\b", r"\bunbearable\b"],
    },
    "Drain Blockage": {
        "primary":   [r"\bdrains?\b", r"\bdrain(?:ing|age)\b", r"\bstormwater\b"],
        "secondary": [r"\bmosquito breeding\b", r"\bblocked\b"],
    },
}

# Rule 4, second sentence — a mention that only locates a complaint is not
# evidence about what is damaged. Heritage Damage therefore needs a heritage
# subject AND explicit damage to it, and never fires on a bare location phrase.
HERITAGE_SUBJECT = [r"\bheritage\b", r"\bhistoric(?:al)?\b", r"\bancient\b",
                    r"\bmuseum\b", r"\bstep well\b", r"\btram road\b"]
HERITAGE_DAMAGE = [r"\bknocked over\b", r"\bdefaced\b", r"\bbroken(?: up)?\b",
                   r"\bdamaged?\b", r"\bnot (?:restored|replaced)\b",
                   r"\bremoved\b", r"\bsubsid(?:ed|ence)\b", r"\bsplit\b"]
HERITAGE_LOCATION_ONLY = [r"\bheritage (?:area|zone|precinct|street)\b",
                          r"\bnear\b.{0,20}\bmuseum\b"]

# The README fixes only the Urgent trigger. Standard against Low is this file's
# call: stated harm, risk or loss of a service is Standard, nuisance without
# stated harm is Low. days_open is never consulted — see agents.md context.
SUPPORTING_SIGNALS = [
    r"\brisk\b", r"\bunsafe\b", r"\bdanger(?:ous)?\b", r"\baccident\b",
    r"\bhealth\b", r"\bstranded\b", r"\bblocked\b", r"\bdengue\b",
    r"\bgas leak\b", r"\bstructural\b", r"\blosses\b", r"\bexposed\b",
]

# Rule 1 is only a rule if it is checked. Refuse to start if the cue table names
# a category the enum does not contain.
_UNKNOWN = set(CATEGORY_CUES) - set(CATEGORIES)
if _UNKNOWN:
    raise SystemExit(f"CATEGORY_CUES names categories outside the enum: {sorted(_UNKNOWN)}")


def _hits(patterns, text):
    """Return the words in `text` literally matched by `patterns`."""
    found = []
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            found.append(m.group(0).strip())
    return found


def classify_complaint(row: dict) -> dict:
    """Classify one complaint row. Returns complaint_id, category, priority, reason, flag."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not complaint_id or not description:
        missing = "complaint_id" if not complaint_id else "description"
        return {"complaint_id": complaint_id or "UNKNOWN", "category": "Other",
                "priority": "Standard", "flag": "NEEDS_REVIEW",
                "reason": f"Row could not be classified: {missing} is missing or blank."}

    # Rule 2 — severity decides priority; nothing below may downgrade a match.
    severity_hits = [(name, _hits([pat], description)[0])
                     for name, pat in SEVERITY_PATTERNS.items()
                     if re.search(pat, description, re.IGNORECASE)]
    if severity_hits:
        priority = "Urgent"
    elif _hits(SUPPORTING_SIGNALS, description):
        priority = "Standard"
    else:
        priority = "Low"

    # Rule 4 — weighted scores, then look for a genuine tie.
    scores, weights = {}, {}
    for cat, cues in CATEGORY_CUES.items():
        primary, secondary = _hits(cues["primary"], description), _hits(cues["secondary"], description)
        scores[cat] = primary + secondary
        weights[cat] = 2 * len(primary) + len(secondary)

    subject, damage = _hits(HERITAGE_SUBJECT, description), _hits(HERITAGE_DAMAGE, description)
    if subject and damage and not _hits(HERITAGE_LOCATION_ONLY, description):
        scores["Heritage Damage"] = subject + damage
        weights["Heritage Damage"] = 2 * len(subject) + len(damage)
    else:
        scores["Heritage Damage"], weights["Heritage Damage"] = [], 0

    ranked = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
    top = ranked[0][1]
    tied = [c for c, w in ranked if w == top]

    flag = ""
    if top == 0:
        category, cited, flag = "Other", [], "NEEDS_REVIEW"
    elif len(tied) > 1:
        category, cited, flag = "Other", scores[tied[0]], "NEEDS_REVIEW"
    else:
        category, cited = ranked[0][0], scores[ranked[0][0]]

    # Rule 3 — the reason must quote words literally present in this description.
    if flag and top == 0:
        reason = (f"No category cue found in \"{description[:60].rstrip()}\"; "
                  "referred for review rather than guessed.")
    elif flag:
        reason = (f"Ambiguous between {' and '.join(tied[:3])} — cues "
                  + ", ".join(f"'{w}'" for w in cited[:3])
                  + " support more than one category equally; referred for review.")
    else:
        reason = "Cited " + ", ".join(f"'{w}'" for w in cited[:3]) + f" → {category}."

    if severity_hits:
        terms = ", ".join(f"'{w}'" for _, w in severity_hits[:3])
        reason = reason.rstrip(".") + f"; severity term {terms} present → Urgent."

    # Rule 1 — validate the emitted value, never trust the cue table alone.
    if category not in CATEGORIES:
        reason = f"Category '{category}' is not in the permitted set; referred for review. " + reason
        category, flag = "Other", "NEEDS_REVIEW"

    return {"complaint_id": complaint_id, "category": category,
            "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV. Rule 5: never drop a row."""
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        raise SystemExit(f"Cannot read input file {input_path}: {exc}")

    results = []
    for i, row in enumerate(rows, start=1):
        try:
            results.append(classify_complaint(row))
        except Exception as exc:                       # a bad row never aborts the run
            results.append({"complaint_id": (row.get("complaint_id") or f"ROW_{i}").strip(),
                            "category": "Other", "priority": "Standard",
                            "flag": "NEEDS_REVIEW",
                            "reason": f"Classification failed for this row: {exc}."})

    fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r["flag"])
    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    print(f"Rows in: {len(rows)}  out: {len(results)}  Urgent: {urgent}  flagged: {flagged}")
    return {"rows": len(results), "flagged": flagged, "urgent": urgent}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
