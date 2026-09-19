"""
UC-0A — Complaint Classifier

Rule-based classifier driven by the enforcement rules in agents.md:
  * category comes from a fixed weighted keyword table (no free wording → no taxonomy drift)
  * severity keywords force Urgent (no severity blindness)
  * every row carries a one-sentence reason quoting the words that decided it
  * weak or tied evidence is flagged NEEDS_REVIEW instead of being presented as confident
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

# (regex, weight) per category. Weight 3 = defining word, 2 = strong, 1 = supporting.
# A category needs a total of at least MIN_CONFIDENT_SCORE to be reported without a flag.
CATEGORY_RULES = {
    "Pothole": [
        (r"\bpotholes?\b", 3),
    ],
    "Flooding": [
        (r"\bflood(?:ed|s)\b", 3),
        (r"\bflooding\b(?!\s+risk)", 3),
        (r"\bflooding\s+risk\b", 1),        # a risk of flooding is not flooding yet
        (r"\bwaterlogg\w*", 3),
        (r"\binundat\w*", 3),
        (r"\bknee-deep\b", 1),
        (r"\brainwater\b", 1),
        (r"\bstanding in water\b", 1),
    ],
    "Streetlight": [
        (r"\bstreet\s?lights?\b", 3),
        (r"\blights?\s+out\b", 3),
        (r"\bunlit\b", 3),
        (r"\blamp\s?posts?\b", 2),
        (r"\bdark(?:ness)?\b", 1),
        (r"\bwiring\b", 1),
        (r"\bsubstation\b", 1),
    ],
    "Waste": [
        (r"\bwaste\b", 3),
        (r"\bgarbage\b", 3),
        (r"\bdead animal\b", 3),
        (r"\bdumped\b", 2),
        (r"\bbins?\b", 1),
        (r"\boverflow\w*", 1),
    ],
    "Noise": [
        (r"\bnoise\b", 3),
        (r"\bmusic\b", 3),
        (r"\bamplifiers?\b", 3),
        (r"\bloudspeakers?\b", 3),
        (r"\bdrilling\b", 3),
        (r"\bhonking\b", 3),
        (r"\bband playing\b", 2),
        (r"\baudible\b", 2),
        (r"\bidling\b", 1),
    ],
    "Road Damage": [
        (r"\bcollaps\w*", 3),
        (r"\bmanholes?\b", 3),
        (r"\broad surface\b", 2),
        (r"\bcracked\b", 2),
        (r"\bsinking\b", 2),
        (r"\bsubsid\w*", 2),
        (r"\bbuckled\b", 2),
        (r"\bfootpath\b", 2),
        (r"\bpaving\b", 2),
        (r"\btiles\b", 1),
        (r"\bupturned\b", 1),
        (r"\bcrater\b", 1),
        (r"\bstructural\b", 1),
    ],
    "Heritage Damage": [
        (r"\bdefaced\b", 3),
        (r"\bhistoric\b", 2),
        (r"\bcobblestones?\b", 2),
        (r"\bheritage\b", 1),               # alone it is usually just the setting
        (r"\bancient\b", 1),
        (r"\bstep well\b", 1),
        (r"\bstone\b", 1),
    ],
    "Heat Hazard": [
        (r"\d+\s*°\s*c\b", 3),
        (r"\bmelting\b", 2),
        (r"\btemperatures?\b", 2),
        (r"\bheat\b", 2),
        (r"\bheatwave\b", 1),
        (r"\bbubbling\b", 1),
        (r"\bsun\b", 1),
        (r"\bburns?\b", 1),
    ],
    "Drain Blockage": [
        (r"\bdrains?\b[^.]{0,40}?\bblock\w*", 2),
        (r"\bblock\w*\s+drains?\b", 2),
        (r"\bstormwater\b", 1),
        (r"\bmosquito\w*", 1),
    ],
}
MIN_CONFIDENT_SCORE = 2

# Severity keywords from the README (stems, so injured/children/hospitalised/collapsed match),
# plus explicit danger-to-person phrases added during CRAFT testing.
SEVERITY_PATTERNS = [
    r"\binjur\w*", r"\bchild\w*", r"\bschools?\b", r"\bhospital\w*", r"\bambulance\w*",
    r"\bfire\b", r"\bhazard\w*", r"\bfell\b", r"\bcollaps\w*",
    r"\bburns?\b", r"\bgas leak\b", r"\blives at risk\b",
]
# Words that show real-world impact; they keep a nuisance complaint at Standard instead of Low.
RISK_PATTERNS = [
    r"\brisk\w*", r"\bunsafe\b", r"\bdanger\w*", r"\baccident\w*", r"\bhealth\b",
    r"\bstranded\b", r"\bsparking\b", r"\bdengue\b", r"\bsubsid\w*", r"\bstructural\b",
]
# Categories that are nuisance/amenity by nature → Low unless impact words are present.
LOW_ELIGIBLE = {"Noise", "Heritage Damage"}


def _find(patterns, text):
    """Return the literal words from text matched by any pattern, in order of appearance."""
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append((m.start(), m.group(0)))
    hits.sort()
    seen, words = set(), []
    for _, w in hits:
        if w.lower() not in seen:
            seen.add(w.lower())
            words.append(w)
    return words, (hits[0][0] if hits else None)


def _score_categories(description):
    scores = {}
    for category, rules in CATEGORY_RULES.items():
        total, words, first_pos = 0, [], None
        for pat, weight in rules:
            for m in re.finditer(pat, description, flags=re.IGNORECASE):
                total += weight
                words.append((m.start(), m.group(0)))
        if total:
            words.sort()
            first_pos = words[0][0]
            scores[category] = (total, first_pos, [w for _, w in words])
    return scores


def _quote(words):
    return ", ".join(f"'{w}'" for w in words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing, so no category or severity could be read from the complaint.",
            "flag": "NEEDS_REVIEW",
        }

    # --- category -----------------------------------------------------------
    scores = _score_categories(description)
    flag, flag_why = "", ""
    if not scores:
        category, cat_words = "Other", []
        flag, flag_why = "NEEDS_REVIEW", "no category keyword matched"
    else:
        # highest score wins; on a tie, the category mentioned first in the text wins
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
        category, (top_score, _, cat_words) = ranked[0]
        if len(ranked) > 1 and ranked[1][1][0] == top_score:
            flag = "NEEDS_REVIEW"
            flag_why = f"it matches {category} and {ranked[1][0]} equally"
        elif top_score < MIN_CONFIDENT_SCORE:
            flag = "NEEDS_REVIEW"
            flag_why = f"the only evidence for {category} is weak"

    assert category in ALLOWED_CATEGORIES

    # --- priority -----------------------------------------------------------
    severity_words, _ = _find(SEVERITY_PATTERNS, description)
    risk_words, _ = _find(RISK_PATTERNS, description)
    if severity_words:
        priority = "Urgent"
        why_priority = f"marked Urgent for severity words {_quote(severity_words)}"
    elif category in LOW_ELIGIBLE and not risk_words:
        priority = "Low"
        why_priority = "set Low as a nuisance/amenity issue with no severity or risk words"
    else:
        priority = "Standard"
        if risk_words:
            why_priority = f"kept Standard because {_quote(risk_words)} shows impact but no severity keyword is present"
        else:
            why_priority = "kept Standard because no severity keyword is present"

    # --- reason (one sentence) ----------------------------------------------
    if cat_words:
        why_category = f"{category} because the description says {_quote(cat_words)}"
    else:
        why_category = "Other because no listed category word appears in the description"
    reason = f"Classified as {why_category}, {why_priority}"
    if flag:
        reason += f"; flagged for review because {flag_why}"
    reason += "."

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
    Flags bad rows instead of crashing and always writes one output row per input row.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "description" not in reader.fieldnames:
                sys.exit(f"Refusing: {input_path} has no 'description' column.")
            rows = list(reader)
    except FileNotFoundError:
        sys.exit(f"Refusing: input file not found: {input_path}")

    results = []
    for i, row in enumerate(rows, start=1):
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # one bad row must not stop the batch
            results.append({
                "complaint_id": (row.get("complaint_id") or f"row-{i}"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row could not be classified ({type(exc).__name__}: {exc}).",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    urgent = sum(r["priority"] == "Urgent" for r in results)
    flagged = sum(r["flag"] == "NEEDS_REVIEW" for r in results)
    print(f"Classified {len(results)} rows: {urgent} Urgent, {flagged} flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
