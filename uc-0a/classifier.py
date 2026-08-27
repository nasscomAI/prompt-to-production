"""
UC-0A — Complaint Classifier

Built from the RICE contract in agents.md and the skill specs in skills.md.
Deterministic, rule-based: no network/LLM calls, runs with only the stdlib so it
works in any workshop environment.

Enforcement encoded here (see agents.md):
  - category is EXACTLY one of the ten allowed strings (taxonomy drift guard)
  - priority is Urgent whenever a severity keyword appears (severity blindness guard)
  - reason always cites specific words copied from the description
  - no invented sub-categories; unmatched -> Other
  - genuine ambiguity (0 matches, or a tie between categories) -> flag NEEDS_REVIEW
"""
import argparse
import csv
import re

# --- Fixed taxonomy: allowed category strings, verbatim (order = tie-break priority) ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Keyword signals per category. Matched case-insensitively as whole words.
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "potholes"],
    "Flooding":        ["flood", "flooding", "flooded", "waterlogging", "waterlogged", "inundated"],
    "Streetlight":     ["streetlight", "street light", "street lamp", "lamp post", "lamppost", "light pole"],
    "Waste":           ["garbage", "waste", "trash", "rubbish", "litter", "dump", "dumping", "sewage overflow"],
    "Noise":           ["noise", "loud", "loudspeaker", "blaring", "honking", "disturbance"],
    "Road Damage":     ["road damage", "cracked road", "broken road", "crumbling", "damaged road", "road surface", "crack"],
    "Heritage Damage": ["heritage", "monument", "historic", "statue", "fort", "temple wall", "heritage site"],
    "Heat Hazard":     ["heat", "heatwave", "heat wave", "no shade", "melting", "scorching"],
    "Drain Blockage":  ["drain", "drainage", "blocked drain", "clogged", "sewer", "manhole", "gutter"],
}

# Severity keywords that MUST force Urgent (agents.md / README).
# Inflections added so "children"/"injuries"/"collapsed" still trigger Urgent.
SEVERITY_KEYWORDS = [
    "injury", "injuries", "child", "children", "school", "schools",
    "hospital", "ambulance", "fire", "hazard", "hazardous",
    "fell", "collapse", "collapsed", "collapsing",
]

# Light signals for the Standard vs Low split (Urgent is decided separately).
LOW_KEYWORDS = ["minor", "small", "cosmetic", "faded", "slightly", "occasional"]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _found(keywords, text):
    """
    Return the list of keywords that appear in text as whole words, tolerating a
    simple plural 's' (so "streetlights"/"floods"/"potholes" still match).
    """
    hits = []
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"s?\b", text):
            hits.append(kw)
    return hits


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    Reflects the enforcement rules in agents.md.
    """
    cid = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Empty description -> cannot classify; flag for review (skills.md error_handling).
    if not description:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty, so no category could be determined from the text.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # --- Category: score each allowed category by keyword hits ---
    scores = {}
    hits_by_cat = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        hits = _found(kws, text)
        if hits:
            scores[cat] = len(hits)
            hits_by_cat[cat] = hits

    flag = ""
    if not scores:
        # No allowed category fits -> Other, and flag as ambiguous.
        category = "Other"
        matched_words = []
        flag = "NEEDS_REVIEW"
    else:
        top = max(scores.values())
        winners = [c for c in ALLOWED_CATEGORIES if scores.get(c) == top]
        category = winners[0]  # deterministic tie-break by taxonomy order
        matched_words = hits_by_cat[category]
        # Genuine ambiguity: two different categories tie on the top score.
        if len(winners) > 1:
            flag = "NEEDS_REVIEW"

    # --- Priority: severity keywords force Urgent ---
    severity_hits = _found(SEVERITY_KEYWORDS, text)
    if severity_hits:
        priority = "Urgent"
    elif _found(LOW_KEYWORDS, text):
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason: must cite specific words from the description ---
    cited = matched_words + severity_hits
    if cited:
        quoted = ", ".join(f'"{w}"' for w in dict.fromkeys(cited))  # dedupe, keep order
        reason = f"Classified as {category} ({priority}) based on the words {quoted} in the description."
    else:
        # Category is Other with no keyword hits: cite the opening of the text itself.
        snippet = " ".join(description.split()[:8])
        reason = f'No taxonomy keyword matched; description reads "{snippet}...", so it is Other and needs review.'

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a single bad row; always writes an output file.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f_in:
        rows = list(csv.DictReader(f_in))

    results = []
    ok, failed = 0, 0
    for i, row in enumerate(rows):
        try:
            results.append(classify_complaint(row))
            ok += 1
        except Exception as exc:  # keep going; flag the row rather than dropping it
            failed += 1
            results.append({
                "complaint_id": (row.get("complaint_id") or f"row_{i}").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row could not be processed ({type(exc).__name__}); flagged for manual review.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {ok} row(s), {failed} flagged on error, {len(results)} total.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
