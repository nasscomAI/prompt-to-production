"""
UC-0A — Complaint Classifier

Deterministic, rule-based classifier for citizen complaints.

Enforcement (mirrors README.md schema — do not drift):
  category  ∈ {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
               Heritage Damage, Heat Hazard, Drain Blockage, Other}
  priority  ∈ {Urgent, Standard, Low}
              Urgent iff a severity keyword is present in the description.
  reason    One sentence, citing specific words from the description.
  flag      "NEEDS_REVIEW" when the category is genuinely ambiguous
            (no signal, or two competing categories), else blank.

The rules live in code so the output is repeatable and auditable — the same
row always yields the same classification.
"""
import argparse
import csv
import re
import sys

# --- Allowed vocabularies (exact strings only) -------------------------------

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST force priority = Urgent (README schema).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category detection keywords. Order matters only as tie-break specificity:
# more specific / distinctive categories are listed first so that when two
# categories tie we still record the ambiguity but prefer the specific one.
# Each entry: (category, [keyword patterns as plain lowercase substrings]).
CATEGORY_KEYWORDS = [
    ("Heritage Damage", ["heritage", "monument", "historic"]),
    ("Heat Hazard",     ["heatwave", "heat wave", "heat hazard", "extreme heat",
                         "melting", "heatstroke", "storing heat", "dangerous temperature",
                         "temperature unbearable", "surface temperature", "°c", "degrees",
                         "burns on contact", "exposed to full sun", "reaching dangerous"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "drain is block",
                         "drain choked", "sewage", "clogged drain", "drain blocked"]),
    ("Pothole",         ["pothole", "pot hole"]),
    ("Flooding",        ["flood", "waterlogged", "water logging", "knee-deep",
                         "knee deep", "inundat", "submerged"]),
    ("Streetlight",     ["streetlight", "street light", "street-light",
                         "lights out", "light out", "lamp", "flickering",
                         "lighting", "lights not working", "unlit", "no lighting",
                         "dark after", "wiring theft"]),
    ("Noise",           ["noise", "loud", "music", "loudspeaker", "blaring",
                         "honking"]),
    ("Waste",           ["garbage", "trash", "litter", "waste", "dumped",
                         "dumping", "dead animal", "bins", "overflowing garbage",
                         "debris"]),
    ("Road Damage",     ["road surface", "road cracked", "cracked", "sinking",
                         "manhole", "footpath", "tiles broken", "broken tiles",
                         "road damage", "sunken", "caved", "subsidence",
                         "paving", "upturned paving", "broken bench"]),
]


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def _find_severity(desc_lower: str):
    """Return the list of severity keywords present in the description."""
    hits = []
    for kw in SEVERITY_KEYWORDS:
        # Word-boundary match so 'fell' doesn't fire on 'fellow', etc.
        if re.search(r"\b" + re.escape(kw), desc_lower):
            hits.append(kw)
    return hits


def _find_categories(desc_lower: str):
    """
    Return list of (category, [matched_words]) for every category with a hit,
    in the specificity order of CATEGORY_KEYWORDS.
    """
    matches = []
    for category, keywords in CATEGORY_KEYWORDS:
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            matches.append((category, matched))
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    Never raises on bad input — degrades to Other / NEEDS_REVIEW instead.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = row.get("description")
    desc_lower = _norm(description)

    # --- Guard: missing / empty description --------------------------------
    if not desc_lower:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty; cannot classify from text alone.",
            "flag": "NEEDS_REVIEW",
        }

    severity_hits = _find_severity(desc_lower)
    category_matches = _find_categories(desc_lower)

    # --- Category decision --------------------------------------------------
    flag = ""
    if not category_matches:
        category = "Other"
        matched_words = []
        flag = "NEEDS_REVIEW"
    else:
        category, matched_words = category_matches[0]
        if len(category_matches) > 1:
            # Two or more distinct categories fired -> genuinely ambiguous.
            flag = "NEEDS_REVIEW"

    # --- Priority decision --------------------------------------------------
    if severity_hits:
        priority = "Urgent"
    elif category == "Noise":
        # Nuisance-class complaint with no severity signal.
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason (must cite specific words from the description) --------------
    cited = matched_words + [w for w in severity_hits if w not in matched_words]
    if cited:
        quoted = ", ".join(f"'{w}'" for w in cited)
        if flag == "NEEDS_REVIEW" and len(category_matches) > 1:
            others = ", ".join(c for c, _ in category_matches[1:])
            reason = (f"Classified as {category} on {quoted}; overlaps with "
                      f"{others}, so flagged for review.")
        else:
            reason = f"Classified as {category} based on {quoted} in the description."
    else:
        reason = f"No known category keywords matched; defaulted to {category}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> int:
    """
    Read input CSV, classify each row, write results CSV.

    Robustness contract:
      - Produces output even if individual rows fail.
      - Never crashes on a bad row; degrades that row to Other/NEEDS_REVIEW.
    Returns the number of rows written.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    written = 0

    try:
        infile = open(input_path, newline="", encoding="utf-8-sig")
    except OSError as e:
        print(f"ERROR: cannot open input '{input_path}': {e}", file=sys.stderr)
        raise SystemExit(1)

    with infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as e:  # last-resort guard — one bad row must not abort the batch
                result = {
                    "complaint_id": (row.get("complaint_id") or f"row_{i}").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed ({type(e).__name__}); needs manual review.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)
            written += 1

    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    count = batch_classify(args.input, args.output)
    print(f"Done. Classified {count} rows. Results written to {args.output}")
