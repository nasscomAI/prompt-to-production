"""
UC-0A — Complaint Classifier
Deterministic, offline complaint classifier built from the approved agents.md
and skills.md for UC-0A. No external APIs, LLM calls, network, or extra packages.

Entry point (see uc-0a/README.md):
    python classifier.py --input <test_[city].csv> --output <results_[city].csv>
"""

import argparse
import csv

# --- Allowed category enum (exact strings) ---
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

# --- Mandatory severity keywords (any occurrence forces Urgent) ---
SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

# --- Traceable category keyword maps ---
# For each allowed category (except Other), a list of tokens that, when found in
# the description/location, constitute a defensible textual basis for that
# category. Matching is case-insensitive substring matching (see _contains_any).
# Tokens are kept specific to avoid false positives from incidental words.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "submerg", "waterlog", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "street lamp", "lights out", "light out", "unlit", "lamppost", "lamp post"],
    "Waste": ["waste", "garbage", "rubbish", "trash", "overflowing", "dead animal", "bulk waste"],
    "Noise": ["noise", "music", "amplifier", "drilling", "band", "loud", "idling"],
    "Road Damage": ["road surface", "cracked", "sinking", "buckled", "subsid", "crater", "footpath", "paving", "tarmac", "cobblestone", "road collapsed", "road subsided", "road buckled"],
    "Heritage Damage": ["heritage", "historic", "monument", "museum", "ancient"],
    "Heat Hazard": ["heat", "temperature", "melting", "burns"],
    "Drain Blockage": ["drain", "gully", "water channel"],
}

# Tokens that indicate an explicitly low-importance / cosmetic / routine matter.
LOW_IMPORTANCE_KEYWORDS = [
    "cosmetic",
    "routine",
    "aesthetic",
    "minor",
    "grass dying",
    "dead grass",
    "not urgent",
    "no risk",
]


def _lower(text):
    return (text or "").lower()


def _contains_any(text, tokens):
    """Return True if any token appears as a substring (case-insensitive).

    Substring matching is used because the controlled dataset's tokens are
    high-precision, and it correctly catches plurals and morphological variants
    (e.g. "potholes", "streetlights", "hospitalised" from "hospital"), which
    strict whole-word boundaries would miss.
    """
    text = _lower(text)
    for token in tokens:
        if _lower(token) in text:
            return True
    return False


def _has_severity(description):
    """Return True if description contains any mandatory severity keyword."""
    return _contains_any(description, SEVERITY_KEYWORDS)


def _traceable_categories(description, location, ward, city):
    """Return the set of allowed categories with a traceable textual basis.

    Uses the description as the primary signal and location/ward/city only where
    they are legitimately relevant (e.g. the word 'heritage' in a location).
    """
    fields = [description, location, ward, city]
    matches = set()
    for field in fields:
        for category, tokens in CATEGORY_KEYWORDS.items():
            if _contains_any(field, tokens):
                matches.add(category)
    return matches


def _assign_category(description, location, ward, city):
    """Choose the category per agents.md Rule 4 (traceable textual basis).

    Returns (category, flagged) where flagged indicates NEEDS_REVIEW is warranted.
    - If no allowed category has a traceable basis -> Other + flagged.
    - If exactly one has a traceable basis -> that category, not flagged.
    - If "Pothole" is explicitly present -> Pothole dominates its broader
      categories (Road Damage / Flooding) because "pothole" is the explicit,
      specific thing named; not flagged.
    - Otherwise several categories are traceable/equally plausible -> pick one
      deterministically but flag NEEDS_REVIEW (agents.md Rule 5).
    """
    matches = _traceable_categories(description, location, ward, city)

    if not matches:
        return "Other", True

    if len(matches) == 1:
        return next(iter(matches)), False

    # Pothole is explicit and specific; it dominates broader categories.
    if "Pothole" in matches:
        return "Pothole", False

    # Multiple distinct allowed categories are traceable / equally plausible.
    best = _pick_best_category(matches, description)
    return best, True


def _pick_best_category(matches, description):
    """Deterministically pick one allowed category from a degree-ambiguous set.

    Prefers categories whose tokens are strongest/most central in the
    description. Used only for ambiguous cases that still warrant NEEDS_REVIEW.
    """
    # Stable ordering by specificity so output is deterministic.
    order = [
        "Pothole",
        "Drain Blockage",
        "Flooding",
        "Streetlight",
        "Noise",
        "Waste",
        "Heat Hazard",
        "Heritage Damage",
        "Road Damage",
    ]
    for cat in order:
        if cat in matches:
            return cat
    return next(iter(matches))


def _classify_priority(description):
    """Assign priority per agents.md Rule 2.

    - Urgent if any severity keyword is present (mandatory).
    - Otherwise Standard by default; Low only for explicitly low-importance,
      cosmetic, routine, or non-hazardous matters.
    - Never derived from days_open/date_raised/reported_by.
    """
    if _has_severity(description):
        return "Urgent"
    if _contains_any(description, LOW_IMPORTANCE_KEYWORDS):
        return "Low"
    return "Standard"


def _one_sentence_reason(description, category, priority):
    """Build a single-sentence reason that quotes specific words from the
    description to justify both the category and the priority."""
    desc = _lower(description or "").strip()
    if not desc:
        return "Category, priority, and flag set to defaults because the description is empty or unusable."

    # Choose a short quoted snippet of the description as evidence.
    snippet = _evidence_snippet(description)

    if priority == "Urgent":
        sev_word = _first_severity_word(description)
        if sev_word:
            return (
                f"Classified as {category} and Urgent because the description "
                f"contains the severity word \"{sev_word}\" in \"{snippet}\"."
            )
        return (
            f"Classified as {category} and Urgent because \"{snippet}\" indicates an acute hazard."
        )

    return (
        f"Classified as {category} with {priority} priority because "
        f"\"{snippet}\" supports that category and does not contain a severity keyword."
    )


def _evidence_snippet(description):
    """Return a short quoted evidence phrase (specific words) from the description."""
    text = description.strip()
    if len(text) <= 90:
        return text
    return text[:90] + "..." if len(text) > 90 else text


def _first_severity_word(description):
    text = _lower(description or "")
    for kw in SEVERITY_KEYWORDS:
        if _lower(kw) in text:
            return kw
    return None


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns exactly four classification fields: category, priority, reason, flag
    (no complaint_id in this single-row skill's output).

    row: dict with keys complaint_id, date_raised, city, ward, location,
         description, reported_by, days_open.
    """
    description = row.get("description")
    location = row.get("location", "")
    ward = row.get("ward", "")
    city = row.get("city", "")

    # Empty / blank / unusable description -> defaults + NEEDS_REVIEW,
    # never a fabricated category.
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Category, priority, and flag set to defaults because the description is empty or unusable.",
            "flag": "NEEDS_REVIEW",
        }

    category, ambiguous = _assign_category(description, location, ward, city)
    priority = _classify_priority(description)

    # NEEDS_REVIEW when the category cannot be chosen with reasonable confidence
    # using the allowed row information (description primary, location/city/ward
    # where relevant), or when multiple allowed categories are equally plausible.
    flag = "NEEDS_REVIEW" if ambiguous else ""
    reason = _one_sentence_reason(description, category, priority)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write a results CSV.

    The results CSV contains: complaint_id, category, priority, reason, flag.
    complaint_id is preserved for row traceability. Every input row produces a
    corresponding output row (no silent drops). Malformed/empty rows are written
    with best-effort defaults (category Other, priority Standard, flag
    NEEDS_REVIEW) and do not block the rest of the batch.
    """
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError(f"Input file has no header/rows: {input_path}")

        for line_no, raw in enumerate(reader, start=2):
            complaint_id = (raw.get("complaint_id") or "").strip() or f"row_{line_no - 1}"
            result = classify_complaint(raw)
            rows.append(
                {
                    "complaint_id": complaint_id,
                    "category": result["category"],
                    "priority": result["priority"],
                    "reason": result["reason"],
                    "flag": result["flag"],
                }
            )

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processed {len(rows)} rows. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
