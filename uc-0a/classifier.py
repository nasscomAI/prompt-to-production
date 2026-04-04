"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.

Enforcement rules (from agents.md):
  1. Category must be exactly one of the 10 allowed values.
  2. Priority is Urgent if any severity keyword appears in the description.
  3. Reason must cite specific words from the description.
  4. flag=NEEDS_REVIEW when category is genuinely ambiguous or missing.
"""
import argparse
import csv
import sys

# ── Taxonomy ─────────────────────────────────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Enforcement rule 2: severity keywords that always trigger Urgent priority.
URGENT_KEYWORDS = [
    "injury", "injured", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "fall", "collapse", "collapsed",
]

# Category → keyword list; ordered so more-specific phrases come first.
# Matching is case-insensitive substring search on the description.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Pothole": [
        "pothole", "pot hole", "pot-hole", "crater", "deep pit",
        "hole in road", "hole in the road",
    ],
    "Flooding": [
        "flood", "flooded", "flooding", "water logging", "waterlog",
        "waterlogged", "inundated", "inundation", "standing water",
        "submerged", "water stagnation", "overflow", "water on road",
    ],
    "Streetlight": [
        "streetlight", "street light", "street lamp", "lamp post",
        "lamppost", "light not working", "light is out", "no light",
        "dark road", "dark street", "bulb fused", "no electricity",
    ],
    "Waste": [
        "garbage", "waste", "trash", "rubbish", "litter", "dump",
        "dumping", "open dump", "foul smell", "stench", "sewage smell",
        "rotting", "decaying", "waste pile", "garbage heap",
    ],
    "Noise": [
        "noise", "noisy", "loud", "blaring", "honking", "horn",
        "music", "loudspeaker", "construction noise", "sound pollution",
        "disturbance", "racket",
    ],
    "Road Damage": [
        "road damage", "broken road", "cracked road", "road crack",
        "road is broken", "road caved", "road dug", "uneven road",
        "damaged road", "speed breaker", "road cut", "tar", "asphalt",
        "road sunken",
    ],
    "Heritage Damage": [
        "heritage", "monument", "historical", "ancient", "temple wall",
        "heritage site", "old building", "protected structure",
        "heritage structure",
    ],
    "Heat Hazard": [
        "heat", "heatwave", "heat wave", "hot", "sunstroke",
        "sun stroke", "heat stroke", "scorching", "temperature",
        "extreme heat",
    ],
    "Drain Blockage": [
        "drain", "drainage", "blocked drain", "drain block", "drain choke",
        "sewer", "sewage", "manhole", "gutter", "nala", "overflow drain",
        "choked drain",
    ],
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _detect_priority(description: str) -> tuple[str, list[str]]:
    """
    Returns (priority, triggered_keywords).
    Priority is Urgent if any URGENT_KEYWORDS appear; otherwise Standard (long
    description) or Low.
    """
    desc_lower = description.lower()
    triggered = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if triggered:
        return "Urgent", triggered
    # Heuristic: more detailed complaints are Standard; terse ones are Low.
    return ("Standard" if len(description.split()) >= 8 else "Low"), []


def _build_reason(category: str, matched_kws: list[str],
                  priority: str, urgent_kws: list[str]) -> str:
    """
    Build a one-sentence reason that cites specific words from the description
    (Enforcement rule 3).
    """
    cited_cat    = matched_kws[:3]
    cited_urgent = urgent_kws[:2]

    if cited_cat and cited_urgent:
        return (
            f"Classified as '{category}' based on keywords {cited_cat}; "
            f"priority set to Urgent due to severity indicators {cited_urgent}."
        )
    if cited_cat:
        return (
            f"Classified as '{category}' based on keywords {cited_cat} "
            f"found in the description."
        )
    if cited_urgent:
        return (
            f"Category could not be determined from description; "
            f"priority set to Urgent due to severity indicators {cited_urgent}."
        )
    return (
        "Description did not match any known category keywords; "
        "flagged for manual review."
    )


# ── Core skills ───────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict with keys 'complaint_id' (str) and 'description' (str)
    Output: dict with keys complaint_id, category, priority, reason, flag

    Enforcement (agents.md):
    - Category is exactly one of the 10 allowed values.
    - Priority is Urgent when any severity keyword is present.
    - Reason cites specific words from the description.
    - flag=NEEDS_REVIEW when category is genuinely ambiguous or empty.
    """
    complaint_id = str(row.get("complaint_id", "UNKNOWN")).strip()
    description  = str(row.get("description",  "")).strip()

    # ── Handle empty description ────────────────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Category detection ──────────────────────────────────────────────────
    all_matches: dict[str, list[str]] = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        found = [kw for kw in keywords if kw in desc_lower]
        if found:
            all_matches[cat] = found

    flag = ""
    if len(all_matches) == 0:
        # No keyword matched — cannot determine category (Enforcement rule 4)
        category    = "Other"
        matched_kws: list[str] = []
        flag        = "NEEDS_REVIEW"
    elif len(all_matches) == 1:
        category    = next(iter(all_matches))
        matched_kws = all_matches[category]
    else:
        # Multiple categories matched — pick the one with the most keyword hits,
        # but flag because the complaint is genuinely ambiguous.
        category    = max(all_matches, key=lambda c: len(all_matches[c]))
        matched_kws = all_matches[category]
        flag        = "NEEDS_REVIEW"

    # ── Priority detection ──────────────────────────────────────────────────
    priority, urgent_kws = _detect_priority(description)

    # ── Reason ─────────────────────────────────────────────────────────────
    reason = _build_reason(category, matched_kws, priority, urgent_kws)

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

    - Flags rows with missing/empty description as NEEDS_REVIEW.
    - Does not crash on bad rows — logs a warning and continues.
    - Writes partial results even if some rows fail.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results: list[dict] = []
    failed  = 0

    # ── Read input ──────────────────────────────────────────────────────────
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows   = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not read input file: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Classify each row ───────────────────────────────────────────────────
    for i, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as exc:
            complaint_id = row.get("complaint_id", f"row_{i}")
            print(
                f"WARNING: Row {i} (id={complaint_id}) failed — {exc}",
                file=sys.stderr,
            )
            results.append({
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Classification error: {exc}",
                "flag":         "NEEDS_REVIEW",
            })
            failed += 1

    # ── Write output ────────────────────────────────────────────────────────
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaint(s). Failures: {failed}.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
