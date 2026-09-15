"""
UC-0A — Complaint Classifier

Built from the RICE spec in agents.md; every enforcement rule maps to code:

  - category comes ONLY from the description column, against an exact 10-value vocabulary
  - priority is Urgent iff a severity keyword appears in the description, else Standard
  - every row carries a reason that quotes specific words from the description
  - no category keyword matches  -> category "Other" + flag "NEEDS_REVIEW" (refuse, don't guess)
  - tied category scores, or simultaneous flooding + drain-blockage signals
    -> best-matching category + flag "NEEDS_REVIEW"
  - batch_classify never crashes on a bad row; bad rows degrade to Other + NEEDS_REVIEW

Standard library only — runs on Python 3.9+ with no dependencies.
"""
import argparse
import csv
import re

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "pot hole"],
    "Flooding": ["flood", "flooded", "floods", "flooding", "waterlogged", "water logging", "knee-deep", "submerged", "inundated", "rainwater"],
    "Streetlight": ["streetlight", "streetlights", "street light", "lights out", "light out", "lamp", "lamps", "dark at night", "darkness", "unlit", "substation"],
    "Waste": ["garbage", "waste", "bins", "dead animal", "litter", "dump", "dumped"],
    "Noise": ["noise", "music", "band", "loud", "honking", "midnight", "drilling", "idling", "trucks", "amplifier", "amplifiers", "disturbance"],
    "Road Damage": ["road surface", "cracked", "cracking", "sinking", "subsided", "subsidence", "manhole", "footpath", "pavement", "paving", "tiles", "cobblestone", "cobblestones", "crater", "collapse", "collapsed", "glass"],
    "Heritage Damage": ["heritage", "historic"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "extreme temperature", "temperature", "temperatures", "melting", "full sun"],
    "Drain Blockage": ["drain", "draining", "drainage", "drain blocked", "blocked drain", "clogged"],
}

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital", "hospitalised",
    "hospitalized", "ambulance", "fire", "hazard", "fell", "fall", "collapse",
    "collapsed",
]

# Used to break category ties deterministically.
VALID_CATEGORIES = set(CATEGORY_KEYWORDS) | {"Other"}
CATEGORY_ORDER = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]


def _dedupe(seq):
    seen = set()
    out = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _find_phrases(original, keywords):
    """Return actual substrings of `original` matching each keyword (word-boundary),
    preserving original case. Word boundaries prevent e.g. "band" matching
    "abandoned" or "sun" matching "Sunday"."""
    low = original.lower()
    found = []
    for kw in keywords:
        match = re.search(r"\b" + re.escape(kw) + r"\b", low)
        if match:
            start, end = match.span()
            found.append(original[start:end])
    return _dedupe(found)


def classify_complaint(row: dict) -> dict:
    """Label one complaint row. Returns complaint_id, category, priority, reason, flag."""
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    lower = description.lower()

    scores = {category: 0 for category in CATEGORY_KEYWORDS}
    matched_phrases = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        phrases = _find_phrases(description, keywords)
        scores[category] = len(phrases)
        if phrases:
            matched_phrases[category] = phrases

    best_score = max(scores.values())

    if best_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        top = [c for c in scores if scores[c] == best_score]
        category = min(top, key=CATEGORY_ORDER.index)
        flood_hit = scores["Flooding"] > 0
        drain_hit = scores["Drain Blockage"] > 0
        ambiguous = len(top) > 1 or (flood_hit and drain_hit)
        flag = "NEEDS_REVIEW" if ambiguous else ""

    sev_phrases = _find_phrases(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if sev_phrases else "Standard"

    if best_score == 0:
        reason = "No known category keyword found in description."
    else:
        quoted = ", ".join(repr(p) for p in matched_phrases.get(category, []))
        reason = f"Category '{category}' from description words: {quoted}"
    if sev_phrases:
        quoted_sev = ", ".join(repr(p) for p in sev_phrases)
        reason += f"; Urgent from description words: {quoted_sev}"
    if flag:
        reason += "; category ambiguous, flagged NEEDS_REVIEW"
    reason += "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify every non-blank row, write results CSV."""
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        input_fieldnames = reader.fieldnames or []
        rows = list(reader)

    output_fieldnames = input_fieldnames + OUTPUT_FIELDS
    results = []
    skipped = 0

    for row in rows:
        if not any((v or "").strip() for v in row.values()):
            skipped += 1
            continue
        try:
            result = classify_complaint(row)
        except Exception as exc:
            result = {
                "complaint_id": str(row.get("complaint_id", "")).strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Failed to classify: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        out = dict(row)
        out.update(result)
        results.append(out)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)

    urgent = sum(1 for r in results if r.get("priority") == "Urgent")
    flagged = sum(1 for r in results if r.get("flag") == "NEEDS_REVIEW")
    invalid = sorted({r["category"] for r in results} - VALID_CATEGORIES)
    print(f"Classified {len(results)} rows ({skipped} blank rows skipped).")
    print(f"Urgent: {urgent} | NEEDS_REVIEW: {flagged} | invalid categories: {invalid or 'none'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
