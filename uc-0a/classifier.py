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
# no stemming/synonyms/plurals -- word-boundary regex enforces this: e.g.
# "collapse" will NOT match "collapsed", "child" will NOT match "children".
# ---------------------------------------------------------------------------

SEVERITY_KEYWORDS = (
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
)
_SEVERITY_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in SEVERITY_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# Explicit self-described "this is not urgent" language, per agents.md:
# "Priority is Low only when the description explicitly signals the issue
# is minor or non-urgent in the complainant's own words (e.g. 'not urgent',
# 'minor')."
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
# Category detection. Not specified in agents.md/skills.md as a keyword
# list -- this is a judgment-call keyword/phrase matcher consistent with
# each category's obvious real-world meaning. Order does not affect which
# categories are found; all categories are checked against every row so
# genuine multi-category ambiguity can be detected.
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
    ],
    "Road Damage": [
        "road damage", "damaged road", "broken road", "cracked road",
        "road crack", "road cracks", "road caved in", "crumbling road",
        "uneven road", "road is damaged", "road surface", "road collapsed",
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

    Input: dict with at least a 'description' key; other keys pass through
    unused as classification evidence but are preserved in the output.
    Output: the original row's fields plus category, priority, reason, flag.
    Never raises.
    """
    result = dict(row) if isinstance(row, dict) else {}

    raw_description = result.get("description", "")
    description = "" if raw_description is None else str(raw_description)

    # --- Missing / empty / whitespace-only description -------------------
    if description.strip() == "":
        result["category"] = "Other"
        result["priority"] = "Standard"
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = "No description was provided."
        return result

    stripped = description.strip()

    # --- Category detection -----------------------------------------------
    matches = _find_category_matches(stripped)
    word_tokens = re.findall(r"[A-Za-z']+", stripped)

    category = "Other"
    flag = ""
    category_clause = ""

    if len(matches) >= 2:
        # Genuine ambiguity: 2+ categories textually plausible.
        ordered = sorted(matches.items(), key=lambda kv: kv[1][1])  # by position
        category = ordered[0][0]  # best guess = earliest-mentioned category
        cited = ", ".join(f'"{txt}" ({cat})' for cat, (txt, _pos) in ordered)
        category_clause = (
            f"category is a best guess of {category} but flagged for review because the "
            f"description mentions {cited}, which could indicate more than one category"
        )
        flag = "NEEDS_REVIEW"
    elif len(matches) == 1:
        category, (matched_text, _pos) = next(iter(matches.items()))
        category_clause = f'category is {category} because the description mentions "{matched_text}"'
        flag = ""
    else:
        # No category keywords matched.
        if len(word_tokens) <= 2:
            # Too vague/short to support any specific category.
            category = "Other"
            flag = "NEEDS_REVIEW"
            category_clause = (
                f'category is Other and flagged for review because the description '
                f'("{_snippet(stripped)}") is too vague to support any specific category'
            )
        else:
            category = "Other"
            flag = ""
            category_clause = (
                f'category is Other because the description ("{_snippet(stripped)}") '
                f'does not contain wording matching any specific category'
            )

    # --- Priority detection --------------------------------------------------
    priority, priority_clause = _determine_priority(stripped)

    # --- Reason (single sentence citing category + priority evidence) -------
    reason = f"{category_clause[0].upper()}{category_clause[1:]}, and {priority_clause}."

    # --- Enum safety net -------------------------------------------------
    if category not in CATEGORIES:
        category = "Other"
    if priority not in PRIORITIES:
        priority = "Standard"
    if flag not in ("", "NEEDS_REVIEW"):
        flag = ""

    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input_path CSV, classify every row with classify_complaint, write
    output_path CSV.

    Structural failures (missing input file, missing description column)
    fail fast and write nothing. Once processing has started, a single bad
    row is written using the classify_complaint fallback and processing
    continues -- the batch never aborts and never produces a partial file.
    """
    # Let a missing input file raise naturally (FileNotFoundError) before
    # anything is written -- fail fast, write nothing.
    with open(input_path, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if not fieldnames or "description" not in fieldnames:
            raise ValueError(
                f"Structural failure: input file '{input_path}' is missing a "
                f"'description' column. No output written."
            )

        rows = list(reader)

    appended = [c for c in ("category", "priority", "reason", "flag") if c not in fieldnames]
    out_fieldnames = list(fieldnames) + appended

    # Only now that the input has been validated and fully read do we open
    # the output file, so a structural failure never leaves a partial file.
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()

        for row in rows:
            try:
                classified = classify_complaint(row)
            except Exception:
                # A single bad row must never abort the batch. Fall back to
                # the same deterministic fallback classify_complaint uses
                # for missing/unreadable descriptions, preserving whatever
                # original fields were readable.
                classified = dict(row) if isinstance(row, dict) else {}
                classified["category"] = "Other"
                classified["priority"] = "Standard"
                classified["flag"] = "NEEDS_REVIEW"
                classified["reason"] = "No description was provided."

            out_row = {key: classified.get(key, "") for key in out_fieldnames}
            writer.writerow(out_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Done. Results written to {args.output}")
