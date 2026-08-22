"""
UC-0A — Complaint Classifier

Deterministic, rule-based classifier. Every value it can emit is pinned to a constant in
this module, so the taxonomy cannot drift between rows or between runs.

Contract enforced here comes from agents.md / skills.md:
  - category  : exactly one of ALLOWED_CATEGORIES
  - priority  : exactly one of ALLOWED_PRIORITIES; Urgent whenever a severity keyword
                appears in the description (overrides every other priority judgement)
  - reason    : one sentence citing text copied verbatim from the description
  - flag      : NEEDS_REVIEW or empty string
  - row count : output rows == input rows, in input order, no row silently dropped
"""
import argparse
import csv
import sys

OUTPUT_FIELDS = ("complaint_id", "category", "priority", "reason", "flag")

ALLOWED_CATEGORIES = (
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

ALLOWED_PRIORITIES = ("Urgent", "Standard", "Low")

# Substring match, case-insensitive. Substring (not word-boundary) is deliberate:
# "child" must also catch "children", "fell" must catch "fell last week".
SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

LOW_SIGNALS = (
    "minor",
    "cosmetic",
    "slight",
    "faded",
    "aesthetic",
    "non-urgent",
    "suggestion",
    "request for",
)

# Keyword evidence per category. Matched against the lowercased description.
CATEGORY_KEYWORDS = {
    "Pothole": ("pothole", "crater"),
    "Road Damage": (
        "road surface",
        "cracked",
        "crack",
        "sinking",
        "subsid",
        "caved in",
        "footpath",
        "pavement",
        "tiles broken",
        "broken tiles",
        "paving",
        "uneven road",
        "manhole cover",
        "speed breaker",
    ),
    "Drain Blockage": (
        "drain block",
        "blocked drain",
        "drain clogged",
        "clogged drain",
        "drain is blocked",
        "open drain",
        "sewage",
        "sewer",
        "nallah",
        "storm water drain",
        "stormwater",
        "manhole",
    ),
    "Streetlight": (
        "streetlight",
        "street light",
        "street lamp",
        "lamp post",
        "lights out",
        "light out",
        "light not working",
        "lights not working",
        "unlit",
        "no lighting",
    ),
    "Waste": (
        "garbage",
        "trash",
        "rubbish",
        "waste",
        "litter",
        "dumped",
        "dumping",
        "dead animal",
        "overflowing bin",
        "garbage bin",
    ),
    "Heritage Damage": (
        "heritage",
        "monument",
        "historic",
        "wada",
        "fort wall",
        "temple facade",
    ),
    # "sun" alone is deliberately excluded: it would match "Sunday" in waste complaints.
    "Heat Hazard": (
        "heatwave",
        "heat wave",
        "extreme heat",
        "heat stroke",
        "sunstroke",
        "no shade",
        "storing heat",
        "melting",
        "melt",
        "\u00b0c",
        "dangerous temperature",
        "temperature unbearable",
        "surface temperature",
        "bubbling",
        "burns on contact",
        "full sun",
        "direct sun",
        "scorching",
        "sweltering",
    ),
    "Noise": (
        "noise",
        "loud music",
        "loudspeaker",
        "music",
        "dj",
        "honking",
        "past midnight",
        "band playing",
        "drilling",
        "idling",
    ),
    "Flooding": (
        "flood",
        "waterlogg",
        "water logging",
        "knee-deep",
        "knee deep",
        "submerged",
        "standing in water",
        "rainwater",
    ),
}

# Deterministic winner when several categories tie on evidence count.
CATEGORY_PRECEDENCE = (
    "Pothole",
    "Road Damage",
    "Drain Blockage",
    "Streetlight",
    "Waste",
    "Heritage Damage",
    "Heat Hazard",
    "Noise",
    "Flooding",
)

# Defect-over-consequence pairs. When the tie set is exactly one of these, the defect is
# the correct category and the row is NOT ambiguous, so no review flag is raised.
CONSEQUENCE_RESOLUTIONS = {
    frozenset({"Flooding", "Drain Blockage"}): "Drain Blockage",
    frozenset({"Flooding", "Pothole"}): "Pothole",
    # Tarmac melting or bubbling at 45C is a heat problem, not a surfacing defect.
    frozenset({"Road Damage", "Heat Hazard"}): "Heat Hazard",
}

NEEDS_REVIEW = "NEEDS_REVIEW"


def _find_verbatim(description: str, needle: str) -> str:
    """Return the text as it appears in `description`, preserving original casing."""
    idx = description.lower().find(needle)
    if idx == -1:
        return needle
    return description[idx:idx + len(needle)]


def _severity_hits(description: str) -> list:
    lowered = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in lowered]


def _category_scores(description: str) -> dict:
    lowered = description.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in lowered]
        if hits:
            scores[category] = hits
    return scores


def _fallback(complaint_id: str, reason: str) -> dict:
    return {
        "complaint_id": complaint_id or "",
        "category": "Other",
        "priority": "Standard",
        "reason": reason,
        "flag": NEEDS_REVIEW,
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Uses only `description` for the decision and `complaint_id` for identity. days_open,
    reported_by, city, ward, location and date_raised are deliberately ignored: a
    complaint is not urgent because it is old or because a councillor referred it.
    Never raises, never returns None.
    """
    row = row or {}
    complaint_id = str(row.get("complaint_id") or "").strip()
    description = str(row.get("description") or "").strip()

    if not complaint_id and not description:
        return _fallback("", "Row is missing both complaint_id and description, so it cannot be classified.")
    if not complaint_id:
        return _fallback("", "Row has a description but no complaint_id, so it cannot be identified.")
    if not description:
        return _fallback(complaint_id, "Description field is empty, so no category evidence exists.")

    severity = _severity_hits(description)
    low_hits = [kw for kw in LOW_SIGNALS if kw in description.lower()]

    if severity:
        priority = "Urgent"
    elif low_hits:
        priority = "Low"
    else:
        priority = "Standard"

    scores = _category_scores(description)

    if not scores:
        result = _fallback(complaint_id, "No allowed category matches the description, so it needs human review.")
        result["priority"] = priority
        return result

    # Defect beats consequence regardless of how much evidence the consequence has:
    # "drain blocked, bus stand flooded" is Drain Blockage, not Flooding. Applied before
    # scoring so the defect wins even when the consequence matches more keywords.
    for pair, defect in CONSEQUENCE_RESOLUTIONS.items():
        if pair <= scores.keys():
            for consequence in pair - {defect}:
                scores.pop(consequence, None)

    best = max(len(hits) for hits in scores.values())
    tied = {c for c, hits in scores.items() if len(hits) == best}

    flag = ""
    if len(tied) == 1:
        category = next(iter(tied))
    else:
        category = next(c for c in CATEGORY_PRECEDENCE if c in tied)
        flag = NEEDS_REVIEW

    evidence = _find_verbatim(description, scores[category][0])
    reason = f'Description mentions "{evidence}", which maps to {category}'
    if severity:
        reason += f'; priority is Urgent because it contains "{_find_verbatim(description, severity[0])}"'
    elif low_hits:
        reason += f'; priority is Low because it contains "{_find_verbatim(description, low_hits[0])}"'
    if flag:
        others = ", ".join(sorted(tied - {category}))
        reason += f"; flagged because {others} fits the description equally well"
    reason += "."

    result = {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

    # Last-line guard: never emit a value outside the allowed sets.
    if result["category"] not in ALLOWED_CATEGORIES or result["priority"] not in ALLOWED_PRIORITIES:
        return _fallback(complaint_id, "Classifier produced a value outside the allowed schema, so the row needs review.")
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Row count in == row count out, input order preserved. The header is written before any
    row is processed so a partial run still leaves a readable file. A per-row failure is
    written as a flagged Other row and the batch continues.
    """
    try:
        infile = open(input_path, "r", encoding="utf-8", newline="")
    except OSError as exc:
        sys.exit(f"Cannot read input file {input_path}: {exc.strerror}")

    with infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            sys.exit(f"Input file {input_path} is empty.")
        if "description" not in reader.fieldnames:
            sys.exit(
                f"Input file {input_path} has no 'description' column. "
                f"Found: {', '.join(reader.fieldnames)}"
            )

        try:
            outfile = open(output_path, "w", encoding="utf-8", newline="")
        except OSError as exc:
            sys.exit(f"Cannot write output file {output_path}: {exc.strerror}")

        total = 0
        flagged = 0
        failed = 0
        with outfile:
            writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            for row in reader:
                total += 1
                try:
                    result = classify_complaint(row)
                except Exception as exc:  # a bad row must not abort the batch
                    failed += 1
                    rid = str((row or {}).get("complaint_id") or "").strip()
                    print(f"Row {rid or total} failed to classify: {exc}", file=sys.stderr)
                    result = _fallback(rid, f"Classification failed for this row ({type(exc).__name__}), so it needs review.")
                if result["flag"] == NEEDS_REVIEW:
                    flagged += 1
                writer.writerow(result)

    print(f"Processed {total} rows — {flagged} flagged {NEEDS_REVIEW}, {failed} errored.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
