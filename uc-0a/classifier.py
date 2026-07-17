"""
UC-0A - Complaint Classifier

Classifies municipal citizen complaints into a fixed category taxonomy and
a severity-driven priority, per agents.md / skills.md.

Only the `description` field drives classification. All other row fields
pass through unchanged. Standard library only.
"""
import argparse
import csv
import re
import sys


# ---------------------------------------------------------------------------
# Enums (verbatim, per agents.md)
# ---------------------------------------------------------------------------

CATEGORIES = (
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
)

PRIORITIES = ("Urgent", "Standard", "Low")

# ---------------------------------------------------------------------------
# Severity keywords (priority = Urgent). Exact words only, case-insensitive,
# no stemming/synonyms/plurals -- word-boundary regex enforces this.
# ---------------------------------------------------------------------------

SEVERITY_KEYWORDS = (
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
)
_SEVERITY_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in SEVERITY_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# Explicit self-described low-urgency language
LOW_PRIORITY_PHRASES = (
    "not urgent", "non-urgent", "non urgent", "not an emergency",
    "no rush", "not a priority", "low priority", "minor issue", "minor",
    "not serious", "whenever convenient", "whenever possible",
)


def _phrase_pattern(phrase: str) -> re.Pattern:
    """Build a whole-word/whole-phrase, whitespace-flexible regex."""
    words = phrase.split()
    escaped = [re.escape(w) for w in words]
    return re.compile(r"\b" + r"\s+".join(escaped) + r"\b", re.IGNORECASE)


_LOW_PATTERNS = [(_phrase_pattern(p), p) for p in LOW_PRIORITY_PHRASES]

# ---------------------------------------------------------------------------
# Category detection keyword/phrase matcher.
# All categories are checked against every row so genuine multi-category
# ambiguity can be detected.
# ---------------------------------------------------------------------------

CATEGORY_PHRASES = {
    "Pothole": [
        "pothole", "potholes", "pot hole", "pot holes",
    ],
    "Flooding": [
        "flood", "flooding", "flooded", "floods",
        "waterlogged", "water logging", "water-logging",
        "inundated", "inundation", "submerged",
        "standing water", "stagnant water", "water accumulation",
    ],
    "Streetlight": [
        "streetlight", "streetlights", "street light", "street lights",
        "lamp post", "lamppost", "lamp-post", "street lamp",
        "light not working", "light is not working", "light pole",
    ],
    "Waste": [
        "garbage", "trash", "waste", "litter", "rubbish",
        "dumping", "dumped", "overflowing bin", "overflowing garbage",
        "waste bin", "trash can", "waste collection", "uncollected garbage",
    ],
    "Noise": [
        "noise", "noisy", "loud music", "loud speaker", "loudspeaker",
        "honking", "blaring", "loud noise", "noise pollution",
        "drilling",
    ],
    "Road Damage": [
        "road damage", "damaged road", "broken road", "cracked road",
        "road crack", "road cracks", "road caved in", "crumbling road",
        "uneven road", "road is damaged", "road surface", "road collapsed",
        "crater", "collapsed partially",
    ],
    "Heritage Damage": [
        "heritage", "monument", "historic building", "historical building",
        "historical site", "heritage site", "archaeological", "heritage structure",
    ],
    "Heat Hazard": [
        "heat wave", "heatwave", "extreme heat", "scorching heat",
        "sun stroke", "sunstroke", "heat hazard", "heat exhaustion",
        "high temperature", "excessive heat",
    ],
    "Drain Blockage": [
        "drain block", "drain blockage", "blocked drain", "clogged drain",
        "drain is blocked", "drainage block", "drainage blockage",
        "sewer block", "sewer blockage", "clogged sewer", "manhole overflow",
        "drain overflow", "choked drain", "blocked sewer", "drain clogged",
        "drain blocked", "drain completely blocked", "main drain blocked",
        "mosquito breeding",
    ],
}

_CATEGORY_PATTERNS = {
    cat: [(_phrase_pattern(p), p) for p in phrases]
    for cat, phrases in CATEGORY_PHRASES.items()
}


def _snippet(text: str, limit: int = 60) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _find_category_matches(description: str):
    """Return {category: (matched_text, position)} for every category with
    at least one phrase hit in the description."""
    hits = {}
    for cat, patterns in _CATEGORY_PATTERNS.items():
        best = None
        for pattern, _phrase in patterns:
            m = pattern.search(description)
            if m and (best is None or m.start() < best[1]):
                best = (m.group(0), m.start())
        if best is not None:
            hits[cat] = best
    return hits


def _determine_priority(description: str):
    """Returns (priority, reason_clause)."""
    m = _SEVERITY_RE.search(description)
    if m:
        keyword = m.group(0)
        return "Urgent", f'priority is Urgent because the description contains the severity keyword "{keyword}"'

    for pattern, phrase in _LOW_PATTERNS:
        m = pattern.search(description)
        if m:
            return "Low", f'priority is Low because the description explicitly signals it is minor/non-urgent ("{m.group(0)}")'

    return "Standard", "priority is Standard because no severity keywords or explicit low-urgency wording were found"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # Handle missing/empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine category
    cat_hits = _find_category_matches(description)

    if len(cat_hits) == 0:
        category = "Other"
        cat_reason = f'no category keywords matched in: "{_snippet(description)}"'
        flag = ""
    elif len(cat_hits) == 1:
        category = list(cat_hits.keys())[0]
        matched_text = list(cat_hits.values())[0][0]
        cat_reason = f'category is {category} because description contains "{matched_text}"'
        flag = ""
    else:
        # Multiple categories matched -- pick the earliest-appearing one as primary
        # but flag as NEEDS_REVIEW for genuine ambiguity
        sorted_hits = sorted(cat_hits.items(), key=lambda x: x[1][1])
        category = sorted_hits[0][0]
        matched_text = sorted_hits[0][1][0]
        other_cats = [c for c, _ in sorted_hits[1:]]
        cat_reason = (
            f'category is {category} (matched "{matched_text}") '
            f'but also matched {", ".join(other_cats)} -- genuinely ambiguous'
        )
        flag = "NEEDS_REVIEW"

    # Determine priority
    priority, pri_reason = _determine_priority(description)

    # Build combined reason (one sentence)
    reason = f"{cat_reason}; {pri_reason}."

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
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    errors = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    errors.append(f"Row {i}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed: {e}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if errors:
        print(f"Warnings ({len(errors)} rows had issues):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints.")
    if errors:
        print(f"  ({len(errors)} rows had errors — see stderr for details.)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
