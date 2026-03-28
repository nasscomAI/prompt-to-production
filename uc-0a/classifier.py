"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.

Enforcement rules (from agents.md):
  - Category must be exactly one of the 10 allowed values — no variations.
  - Priority is 'Urgent' if any severity keyword is present; 'Standard' or 'Low' otherwise.
  - Every output row includes a reason that cites specific words from the description.
  - Ambiguous categories are flagged NEEDS_REVIEW.
"""
import argparse
import csv
import re
import sys

# ── Allowed taxonomy (exact strings, no variations) ──────────────────────────
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

# ── Severity keywords that MUST trigger Urgent (from agents.md) ───────────────
# Stored as (keyword, use_prefix_match).  use_prefix_match=True lets the regex
# match the keyword at the START of a longer word (e.g. 'hospital' → 'hospitalised').
SEVERITY_KEYWORDS: list[tuple[str, bool]] = [
    ("injury",     False),
    ("child",      False),
    ("school",     False),
    ("hospital",   True),   # also matches 'hospitalised', 'hospitalized'
    ("ambulance",  False),
    ("fire",       False),
    ("hazard",     False),
    ("fell",       False),
    ("collapse",   True),   # also matches 'collapsed'
]

# ── Category keyword map — ordered from most-specific to least-specific ───────
# Each entry: (category_name, [keyword_list])
# ALL keyword matching uses whole-word regex (\b boundaries) to prevent substring
# false positives (e.g. "hot" inside "photographing", "sun" inside "Sunday").
CATEGORY_KEYWORDS = [
    ("Heritage Damage",  ["heritage", "historical", "historic", "monument", "ancient", "archaeological",
                          "listed building", "cobblestone", "heritage stone", "heritage precinct",
                          "heritage area", "heritage zone"]),
    ("Heat Hazard",      ["heat", "temperature", "temperatures", "heatwave", "sun", "hot", "scorching",
                          "thermal", "melting", "burning temperature", "unbearable temperature",
                          "heat island", "full sun", "temperature reads"]),
    ("Drain Blockage",   ["drain", "drainage", "drain blocked", "sewer", "manhole", "gutter blocked",
                          "stormwater drain", "mosquito breeding"]),
    ("Pothole",          ["pothole", "potholes"]),
    ("Flooding",         ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "inundated",
                          "submerged", "water-logged", "floods in"]),
    ("Streetlight",      ["streetlight", "streetlights", "street light", "street lamp", "lamp post",
                          "lights out", "light out", "no lighting", "dark street", "flickering light",
                          "sparking light", "unlit", "lamp knocked", "darkness", "substation tripped",
                          "wiring theft"]),
    ("Waste",            ["garbage", "waste", "rubbish", "refuse", "litter", "dumped", "dump",
                          "overflowing bin", "garbage bin", "waste bin", "dead animal", "carcass",
                          "bulk waste", "renovation waste", "waste overflowing", "waste not cleared",
                          "waste bins", "bins overflowing"]),
    ("Noise",            ["noise", "music", "loud", "sound", "midnight", "late night", "playing music",
                          "party noise", "construction noise", "drilling", "construction drilling",
                          "band", "band playing", "amplifier", "generator noise", "idling engine",
                          "trucks idling"]),
    ("Road Damage",      ["road surface", "cracked road", "sinking", "sunken road", "broken road",
                          "road crack", "footpath", "pavement", "tiles broken", "tiles upturned",
                          "road damage", "utility work", "road repair", "road collapsed", "road subsided",
                          "collapsed road", "crater", "sinkhole", "upturned paving", "road buckled",
                          "surface buckled", "cobblestones broken", "tarmac"]),
]

# ── Fallback broad water keyword — only used after drain/flood pass ───────────
WATER_KEYWORDS = ["water", "standing water", "puddle"]


def _normalise(text: str) -> str:
    """Lowercase and strip punctuation for matching."""
    return text.lower()


def _find_severity_keyword(description: str) -> str | None:
    """Return the first severity keyword found, or None."""
    desc_lower = _normalise(description)
    for kw, prefix_match in SEVERITY_KEYWORDS:
        # prefix_match=True: match keyword at start of a word (e.g. hospital → hospitalised)
        # prefix_match=False: whole-word match only
        suffix = r'' if prefix_match else r'\b'
        if re.search(r'\b' + re.escape(kw) + suffix, desc_lower):
            return kw
    return None


def _score_categories(description: str) -> list[tuple[str, int, list[str]]]:
    """
    Score each category by keyword hits using whole-word regex matching.
    Returns list of (category, score, matched_keywords) sorted descending by score.
    """
    desc_lower = _normalise(description)
    scores = []
    for category, keywords in CATEGORY_KEYWORDS:
        hits = [
            kw for kw in keywords
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)
        ]
        if hits:
            scores.append((category, len(hits), hits))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def _build_reason(category: str, matched_keywords: list[str], severity_kw: str | None,
                  description: str) -> str:
    """Construct a one-sentence reason that cites specific words from the description."""
    # Find the actual phrase in the original description (preserve original casing)
    cited = []
    desc_lower = description.lower()
    for kw in matched_keywords[:2]:  # cite at most two category keywords
        idx = desc_lower.find(kw)
        if idx != -1:
            # Grab a short phrase window around the keyword
            snippet = description[max(0, idx - 5): idx + len(kw) + 20].strip().rstrip(".,;:")
            cited.append(f'"{snippet}"')

    if severity_kw:
        cited.append(f'"{severity_kw}"')

    if cited:
        return f"Classified as {category} because description mentions {', '.join(cited)}."
    # Fallback: quote the first 60 chars
    snippet = description[:60].rstrip()
    return f"Classified as {category} based on description: \"{snippet}\"."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict with at minimum a 'description' key and optionally 'complaint_id'.
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement (agents.md):
      • Category — exactly one of the 10 allowed values.
      • Priority — 'Urgent' if a severity keyword is present, else 'Standard' or 'Low'.
      • Reason   — one sentence citing specific words from the description.
      • Flag     — 'NEEDS_REVIEW' when genuinely ambiguous, else blank.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = (row.get("description") or "").strip()

    # Guard: empty / null description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description is empty or null — cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    # ── Step 1: Detect severity keyword ──────────────────────────────────────
    severity_kw = _find_severity_keyword(description)
    priority = "Urgent" if severity_kw else None  # will resolve to Standard/Low below

    # ── Step 2: Score categories ─────────────────────────────────────────────
    scores = _score_categories(description)

    # ── Step 3: Special case — "water" alone maps to Flooding only if no
    #            Drain Blockage already matched (drain keyword takes precedence)
    if not scores:
        desc_lower = _normalise(description)
        if any(wk in desc_lower for wk in WATER_KEYWORDS):
            scores = [("Flooding", 1, ["water"])]

    # ── Step 4: Determine category + flag ────────────────────────────────────
    flag = ""
    if not scores:
        category         = "Other"
        matched_keywords = []
        flag             = "NEEDS_REVIEW"
    elif len(scores) >= 2 and scores[0][1] == scores[1][1]:
        # Tie between two categories — genuinely ambiguous
        category         = scores[0][0]
        matched_keywords = scores[0][2]
        flag             = "NEEDS_REVIEW"
    else:
        category         = scores[0][0]
        matched_keywords = scores[0][2]

    # ── Special ambiguity: Heritage + Streetlight co-presence ────────────────
    top_names = [s[0] for s in scores[:2]]
    if "Heritage Damage" in top_names and "Streetlight" in top_names:
        flag = "NEEDS_REVIEW"

    # ── Step 5: Resolve Standard vs Low for non-Urgent ───────────────────────
    if not priority:
        if category == "Noise":
            priority = "Low"
        else:
            priority = "Standard"

    # ── Step 6: Build reason sentence ────────────────────────────────────────
    reason = _build_reason(category, matched_keywords, severity_kw, description)

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV at input_path, classify each row, write results to output_path.

    Behaviour (skills.md):
      • Flags null/empty description rows without crashing.
      • Produces an output row for every input row, even on error.
      • Prints a per-row summary to stdout for CRAFT review.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results       = []
    null_rows     = []
    error_rows    = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows   = list(reader)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[ERROR] Could not read {input_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'─'*60}")
    print(f"  UC-0A Complaint Classifier — {len(rows)} rows loaded")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print(f"{'─'*60}\n")

    for i, row in enumerate(rows, start=1):
        complaint_id = row.get("complaint_id", f"ROW-{i}")
        description  = (row.get("description") or "").strip()

        if not description:
            null_rows.append(complaint_id)

        try:
            result = classify_complaint(row)
        except Exception as exc:
            # Never crash the batch — produce a safe fallback row
            result = {
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Classification failed with error: {exc}",
                "flag":         "NEEDS_REVIEW",
            }
            error_rows.append(complaint_id)

        results.append(result)

        # Per-row stdout summary for CRAFT review
        flag_str     = f"  [{result['flag']}]" if result["flag"] else ""
        priority_str = result["priority"].upper()
        print(f"  {complaint_id:<14}  {result['category']:<16}  {priority_str:<8}{flag_str}")
        print(f"    → {result['reason']}")

    # ── Write output CSV ──────────────────────────────────────────────────────
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        print(f"\n[ERROR] Could not write output file: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Summary report ────────────────────────────────────────────────────────
    urgent_count       = sum(1 for r in results if r["priority"] == "Urgent")
    needs_review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"\n{'─'*60}")
    print(f"  DONE — {len(results)} rows classified")
    print(f"  Urgent          : {urgent_count}")
    print(f"  Needs Review    : {needs_review_count}")
    if null_rows:
        print(f"  Null desc rows  : {len(null_rows)} → {', '.join(null_rows)}")
    if error_rows:
        print(f"  Error rows      : {len(error_rows)} → {', '.join(error_rows)}")
    print(f"  Results written : {output_path}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

