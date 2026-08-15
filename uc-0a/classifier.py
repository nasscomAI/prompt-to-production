"""
UC-0A — Complaint Classifier
================================
Classifies citizen complaints from a CSV into an exact taxonomy with
severity-aware priority, a justification reason, and an ambiguity flag.

Enforcement (see agents.md):
- category must be exactly one of the ALLOWED_CATEGORIES strings
- priority is Urgent if any SEVERITY_KEYWORDS appear in the description
- every output row carries a reason citing words from the description
- genuinely ambiguous rows are marked NEEDS_REVIEW, never guessed
"""
import argparse
import csv
import re
import sys

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
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# (category, primary keywords, context keywords, excluded phrases)
# context keywords are required alongside a primary keyword before the
# category counts as a match. Excluded phrases cancel primary keywords
# (e.g. "flooding risk" is a consequence, not an experienced flood).
CATEGORY_RULES = [
    ("Drain Blockage", ("drain", "stormwater"), ("block", "choke", "debris"), ()),
    ("Flooding", ("flood", "submerged", "waterlog", "rainwater"), None,
     ("flooding risk", "risk of flooding", "filling with rainwater")),
    ("Pothole", ("pothole", "pot hole", "pot-hole"), None, ()),
    ("Streetlight", ("streetlight", "street light", "lights out", "unlit", "lamp",
                     "flickering", "sparking", "substation", "darkness", "dark"), None, ()),
    ("Waste", ("garbage", "waste", "rubbish", "litter", "bins", "dead animal",
               "overflow", "dumped", "piles of"), None, ()),
    ("Noise", ("noise", "music", "loud", "amplifier", "band", "drilling",
               "idling", "audible"), None, ()),
    ("Road Damage", ("road surface", "cracked", "sinking", "subsided", "subsidence",
                     "buckled", "collapsed", "footpath", "manhole", "paving",
                     "pavement", "tiles", "cobblestones", "crater", "upturned"), None, ()),
    ("Heritage Damage", ("heritage", "historic", "ancient", "monument"),
     ("heritage concern", "knocked", "defaced", "broken", "restored", "not replaced",
      "removed", "damaged"), ()),
    ("Heat Hazard", ("melting", "temperature", "°c", "burns", "unbearable",
                     "scorching", "heat", "full sun", "bubbling"),
     None, ("heatwave",)),
]

# keywords that legitimately appear as stems inside longer words
# (e.g. flood -> flooded, streetlight -> streetlights); everything else
# must match on word boundaries so "band" never matches "abandoned"
# or "photographs" never triggers a heat hazard via "hot".
STEM_KEYWORDS = {"flood", "streetlight", "overflow", "amplifier", "dark",
                 "pothole", "drain", "waterlog", "lamp", "bins", "°c",
                 "temperature"}

# order used to break ties when two categories score equally
TIE_BREAK_ORDER = ["Pothole", "Flooding", "Drain Blockage", "Streetlight",
                   "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard"]

# purely cosmetic issues (no safety / health / service impact) drop to Low
COSMETIC_KEYWORDS = ("grass", "irrigation", "garden", "aesthetic", "appearance")


def _lower(text: str) -> str:
    return (text or "").lower()


def _kw_in(text: str, keyword: str) -> bool:
    """Word-boundary match, with substring fallback for stem keywords."""
    if keyword in STEM_KEYWORDS:
        return keyword in text
    return re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", text) is not None


def _category_matches(description: str) -> list:
    """Return list of (category, score) that match the description."""
    low = _lower(description)
    matches = []
    for category, primaries, contexts, excluded in CATEGORY_RULES:
        if any(phrase in low for phrase in excluded):
            continue
        score = 0
        for kw in primaries:
            if _kw_in(low, kw):
                score += 1
        if score > 0:
            if contexts is not None:
                context_hits = [ckw for ckw in contexts if ckw in low]
                if not context_hits:
                    continue
                score += len(context_hits)
            matches.append((category, score))
    return matches


def _pick_category(description: str) -> tuple:
    """
    Choose the category for a description.
    Returns (category, flag, reason_note).
    flag is "NEEDS_REVIEW" when the description is genuinely ambiguous
    (two+ competing categories) or maps to no known category (Other).
    """
    low = _lower(description)
    matches = _pick_all_matches(low)
    if not matches:
        return ("Other", "NEEDS_REVIEW", "no category keywords found")
    if len(matches) == 1:
        return (matches[0][0], "", "")
    # two or more categories compete -> genuinely ambiguous
    return (matches[0][0], "NEEDS_REVIEW",
            "ambiguous between " + ", ".join(c for c, _ in matches))


def _pick_all_matches(low: str) -> list:
    """Match categories, sorted by score desc then tie-break order."""
    scored = _category_matches(low)
    ranked = sorted(scored, key=lambda item: (-item[1], _tie_index(item[0])))
    return ranked


def _tie_index(category: str) -> int:
    try:
        return TIE_BREAK_ORDER.index(category)
    except ValueError:
        return len(TIE_BREAK_ORDER)


def _classify_priority(description: str, category: str) -> tuple:
    """
    Priority decision.
    Returns (priority, severity_note).
    Urgent when a severity keyword appears; Low only for purely cosmetic
    complaints; everything else is Standard.
    """
    low = _lower(description)
    hits = [kw for kw in SEVERITY_KEYWORDS if kw in low]
    if hits:
        return ("Urgent", 'severity keyword(s) "%s" present' % ", ".join(hits))
    if category in ("Other",) and any(kw in low for kw in COSMETIC_KEYWORDS):
        return ("Low", "cosmetic issue with no safety or service impact")
    return ("Standard", "no severity keyword and not purely cosmetic")


def _quote_excerpt(description: str, max_len: int = 90) -> str:
    """Short quoted snippet from the description for the reason field."""
    text = (description or "").strip()
    if not text:
        return "no description provided"
    if len(text) <= max_len:
        return '"%s"' % text
    return '"%s..."' % text[:max_len].rstrip()


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip() or "ROW-UNKNOWN"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Category cannot be determined: no description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag, ambiguity_note = _pick_category(description)
    priority, severity_note = _classify_priority(description, category)

    reason = (
        'Category "%s" because description says %s; priority %s because %s.'
        % (category, _quote_excerpt(description), priority.lower(), severity_note)
    )
    if flag == "NEEDS_REVIEW":
        reason = reason + " Flagged NEEDS_REVIEW: " + (ambiguity_note or
                                                       "category could not be determined with confidence.")

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
    Never crashes on a bad row: malformed rows are flagged in the output.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print("Error: input CSV has no header row.", file=sys.stderr)
                sys.exit(1)
            rows = list(reader)
    except FileNotFoundError:
        print("Error: input file not found: %s" % input_path, file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print("Error: cannot read input file %s: %s" % (input_path, exc), file=sys.stderr)
        sys.exit(1)

    headers = rows[0].keys() if rows else []
    out_headers = list(headers) + ["category", "priority", "reason", "flag"]

    processed = 0
    failed = 0
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers, extrasaction="ignore")
        writer.writeheader()
        for i, row in enumerate(rows):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                failed += 1
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip() or ("ROW-%d" % (i + 1)),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be classified: %s" % exc,
                    "flag": "NEEDS_REVIEW",
                }
            out_row = dict(row)
            out_row.update(result)
            writer.writerow(out_row)
            processed += 1

    print("Classified %d rows from %s -> %s (%d row(s) failed and were flagged)."
          % (processed, input_path, output_path, failed))
    return processed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")