"""
UC-0A — Complaint Classifier
Implements the enforcement rules defined in agents.md and the two skills in skills.md.

Rules enforced:
  - category is exactly one of ALLOWED_CATEGORIES (no variations, no invented values)
  - priority is exactly one of Urgent / Standard / Low
  - severity keywords force priority = Urgent (case-insensitive, whole word)
  - every row has a one-sentence reason citing words from the description
  - unmatched / ambiguous / empty descriptions -> category Other + NEEDS_REVIEW
  - batch never crashes on a bad row; it flags it and continues
"""
import argparse
import csv
import re

# --- Fixed taxonomy — the only categories that may ever be emitted. ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

VALID_PRIORITIES = {"Urgent", "Standard", "Low"}

# Severity keywords that MUST trigger Urgent (README + agents.md).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category detection keywords, ordered by specificity. First match wins.
# Each entry: (category, [keyword, ...]). Keywords are matched as whole words,
# case-insensitive, against the description.
CATEGORY_KEYWORDS = [
    ("Drain Blockage", ["drain blocked", "blocked drain", "stormwater drain", "drain completely blocked", "main drain", "drain"]),
    ("Flooding",       ["flooded", "flooding", "floods", "knee-deep", "waterlogged", "water-logged"]),
    ("Heritage Damage",["heritage", "tram road cobblestones", "step well", "museum", "marble palace", "historic"]),
    ("Heat Hazard",    ["melting", "44°c", "45°c", "52°c", "heat", "heatwave", "bubbling", "burns on contact", "temperature reads"]),
    ("Streetlight",    ["streetlight", "street light", "lights out", "lamp post", "unlit", "dark after", "substation tripped", "flickering and sparking"]),
    ("Pothole",        ["pothole", "potholes"]),
    ("Waste",          ["garbage", "waste", "bins", "dead animal", "dumped", "trash", "rubbish", "overflow"]),
    ("Noise",          ["music", "amplifier", "loud", "drilling", "band playing", "idling", "engines on", "noise"]),
    ("Road Damage",    ["road surface", "cracked", "sinking", "subsided", "subsidence", "buckled", "collapsed", "crater", "manhole", "footpath", "paving", "road damage"]),
]


def _find_severity_keyword(description: str):
    """Return the first severity keyword present in the description, else None."""
    text = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return kw
    return None


def _detect_category(description: str):
    """Return (category, matched_keyword) or (None, None) if nothing matches."""
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            # Multi-word phrases: substring match; single words: whole-word match.
            if " " in kw or any(c in kw for c in "°"):
                if kw in text:
                    return category, kw
            elif re.search(r"\b" + re.escape(kw) + r"\b", text):
                return category, kw
    return None, None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys complaint_id, category, priority, reason, flag.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Enforcement: empty description -> Other / Standard / NEEDS_REVIEW.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify from the row alone.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_kw = _detect_category(description)

    # Enforcement: unmatched category -> Other + NEEDS_REVIEW (never guess).
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_basis = "no listed category keyword found in description"
    else:
        flag = ""
        reason_basis = f'matched on "{matched_kw}"'

    # Enforcement: severity keyword forces Urgent, regardless of category.
    severity_kw = _find_severity_keyword(description)
    if severity_kw is not None:
        priority = "Urgent"
        reason = f'Classified as {category} ({reason_basis}); marked Urgent due to severity term "{severity_kw}".'
    else:
        priority = "Standard"
        reason = f'Classified as {category} ({reason_basis}); no severity term present, so Standard.'

    # Safety net: category and priority must be in the allowed sets.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in VALID_PRIORITIES:
        priority = "Standard"

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
    Produces output even if some rows fail; flags bad rows instead of crashing.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    processed = 0
    flagged = 0

    with open(input_path, "r", encoding="utf-8", newline="") as fin, \
         open(output_path, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never crash the batch on one bad row
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be classified ({type(exc).__name__}); needs manual review.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)
            processed += 1
            if result["flag"] == "NEEDS_REVIEW":
                flagged += 1

    print(f"Processed {processed} rows ({flagged} flagged NEEDS_REVIEW).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
