"""
UC-0A — Complaint Classifier
Built following agents.md (RICE) and skills.md enforcement rules.
No external dependencies — uses Python stdlib only.
"""
import argparse
import csv
import sys
from typing import Optional

# ── Schema constants (from UC-0A README) ─────────────────────────────────────
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

# Severity keywords that MUST trigger Urgent (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Category keyword mapping ──────────────────────────────────────────────────
# Each entry: (category_name, [keywords])
# Order matters for tie-breaking — more specific entries first.
# Flooding is listed BEFORE Drain Blockage so flooding wins when both keywords
# are present (e.g. "flooded bus stand, drain blocked").
CATEGORY_RULES = [
    ("Heritage Damage",  ["heritage", "monument", "fort", "historical", "ancient", "heritage street"]),
    ("Heat Hazard",      ["heat", "temperature", "sun", "hot", "heatwave", "dehydration"]),
    ("Flooding",         ["flood", "flooded", "waterlogged", "inundated", "submerged", "knee-deep",
                          "standing water", "overflow water"]),
    ("Drain Blockage",   ["drain blocked", "drain blockage", "blocked drain", "drain clogged",
                          "drainage blocked", "nala blocked", "nala"]),
    ("Pothole",          ["pothole", "pot-hole", "pit", "crater"]),
    ("Streetlight",      ["streetlight", "street light", "lamp post", "light out", "lights out",
                          "sparking", "flickering", "electrical hazard", "no streetlight"]),
    ("Noise",            ["noise", "music", "loud", "sound", "dj", "speaker", "wedding",
                          "midnight", "late night", "blaring"]),
    ("Waste",            ["garbage", "waste", "trash", "rubbish", "litter", "refuse",
                          "dumping", "dumped", "overflowing bin", "dead animal", "rotting",
                          "stench", "smell"]),
    # Road Damage keywords are intentionally specific — avoid matching the word
    # "road" appearing incidentally (e.g. "dumped on public road").
    ("Road Damage",      ["road surface", "road crack", "road damage", "road broken",
                          "sinking road", "cracked road", "road sinking",
                          "pothole road", "damaged road",
                          "footpath", "pavement", "broken tile", "upturned tile",
                          "manhole", "missing cover",
                          "crack", "sinking", "fallen", "collapsed road"]),
]


def _detect_categories(description: str) -> list:
    """Return list of category names that match keywords found in description."""
    desc_lower = description.lower()
    matched = []
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                if category not in matched:
                    matched.append(category)
                break
    return matched


def _detect_priority(description: str) -> tuple:
    """Return (priority, triggered_keyword_or_None)."""
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        # Match whole-word or substring — README says keyword presence is sufficient
        if kw in desc_lower:
            return "Urgent", kw
    return "Standard", None


def _build_reason(description: str, category: str, priority: str,
                  triggered_kw: Optional[str], ambiguous: bool) -> str:
    """
    Build a one-sentence reason that quotes specific words from the description.
    Follows enforcement rule 3: must cite specific words from description.
    """
    # Extract a short representative phrase (first sentence) from description.
    # Use str.replace in a chain — each step's result is unambiguously `str`,
    # avoiding Pyre2's issues with re.split list indexing and re.match slicing.
    desc: str = description.strip().rstrip(".")
    normalized: str = desc.replace("!", ".").replace("?", ".")
    parts: list[str] = normalized.split(".")
    first_sentence: str = parts[0].strip()
    excerpt: str = first_sentence
    if len(first_sentence) > 80:
        excerpt = first_sentence[0:80] + "..."

    if triggered_kw:
        return (
            f"Classified as {category} (Urgent) because description mentions "
            f'"{triggered_kw}" in context: "{excerpt}".'
        )
    if ambiguous:
        return (
            f"Closest match is {category} but category is ambiguous; "
            f'description reads: "{excerpt}".'
        )
    return f'Classified as {category} based on description: "{excerpt}".'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement (agents.md):
    1. Category — exact string from ALLOWED_CATEGORIES only
    2. Priority — Urgent if any SEVERITY_KEYWORD present
    3. Reason   — one sentence quoting specific words from description
    4. Flag     — NEEDS_REVIEW when genuinely ambiguous
    5. No hallucinated sub-categories
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = (row.get("description") or "").strip()

    # ── Guard: missing/empty description ─────────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided.",
            "flag":         "NEEDS_REVIEW",
        }

    # ── Priority (enforcement rule 2) ─────────────────────────────────────────
    priority, triggered_kw = _detect_priority(description)

    # ── Category (enforcement rules 1 & 5) ───────────────────────────────────
    matched_categories = _detect_categories(description)
    ambiguous = False
    flag = ""

    if len(matched_categories) == 0:
        category = "Other"
        # No keywords → genuinely ambiguous
        flag = "NEEDS_REVIEW"
        ambiguous = True
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        # Multiple matches → ambiguous; pick highest-priority match (first per CATEGORY_RULES order)
        for cat, _ in CATEGORY_RULES:
            if cat in matched_categories:
                category = cat
                break
        flag = "NEEDS_REVIEW"
        ambiguous = True

    # Safety net — should never happen, but enforce the schema
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # ── Reason (enforcement rule 3) ───────────────────────────────────────────
    reason = _build_reason(description, category, priority, triggered_kw, ambiguous)

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    skill: batch_classify (skills.md)
    - Produces output even if individual rows fail
    - Failed rows → category=Other, priority=Low, reason="Classification error", flag=NEEDS_REVIEW
    - Logs row-level errors to stderr; never crashes
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_rows = list(reader)

    results = []
    for row in input_rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:  # noqa: BLE001
            complaint_id = row.get("complaint_id", "UNKNOWN")
            print(
                f"[ERROR] Row {complaint_id} failed classification: {exc}",
                file=sys.stderr,
            )
            result = {
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       "Classification error.",
                "flag":         "NEEDS_REVIEW",
            }
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
