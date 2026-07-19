"""
UC-0A — Complaint Classifier
Classifies civic complaints by category, priority, reason, and flag.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# ─── Fixed taxonomy — exactly the 10 allowed categories ────────────────────
CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole", "pot hole", "pot-hole", "tyre damage", "tire damage",
        "crater", "dip in road", "hole in road", "road hole",
    ],
    "Flooding": [
        "flood", "flooded", "waterlogging", "waterlogged", "water logging",
        "submerged", "inundated", "knee-deep", "waist-deep", "stranded",
        "water stagnation", "stagnant water",
    ],
    "Streetlight": [
        "streetlight", "street light", "street-light", "lamp post",
        "lamppost", "lights out", "light out", "bulb", "flickering",
        "sparking", "dark at night", "no light", "not working light",
    ],
    "Waste": [
        "garbage", "waste", "trash", "litter", "rubbish", "dumped",
        "overflowing bin", "overflowing garbage", "dead animal",
        "debris", "refuse", "bulk waste", "solid waste", "sewage smell",
        "smell", "stench",
    ],
    "Noise": [
        "noise", "loud music", "music past midnight", "loudspeaker",
        "honking", "construction noise", "decibel", "sound pollution",
        "noise pollution", "blaring",
    ],
    "Road Damage": [
        "road damage", "road surface", "cracked road", "sinking road",
        "broken road", "road caved", "road cave", "road crack",
        "footpath broken", "footpath tiles", "pavement damage",
        "broken pavement", "upturned", "road sinking",
    ],
    "Heritage Damage": [
        "heritage", "monument", "historical", "historic", "ancient",
        "archaeological", "protected structure", "heritage street",
    ],
    "Heat Hazard": [
        "heat hazard", "heatstroke", "heat stroke", "sunstroke",
        "extreme heat", "heat wave", "heatwave", "heat-related",
        "thermal", "high temperature",
    ],
    "Drain Blockage": [
        "drain block", "drain clog", "blocked drain", "clogged drain",
        "drainage block", "manhole", "sewer block", "sewer overflow",
        "drain overflow", "manholes", "missing manhole", "open drain",
    ],
}

# ─── Severity keywords that MUST trigger Urgent ───────────────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _match_category(description_lower: str) -> tuple[str, list[str]]:
    """
    Match the description against category keywords.
    Returns (best_category, matched_words).
    If tied or no match, returns ("Other", []).
    """
    scores: dict[str, list[str]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in description_lower]
        if matched:
            scores[category] = matched

    if not scores:
        return "Other", []

    # Sort by number of keyword matches, descending
    ranked = sorted(scores.items(), key=lambda x: len(x[1]), reverse=True)

    # If top two categories tie on match count → ambiguous
    if len(ranked) >= 2 and len(ranked[0][1]) == len(ranked[1][1]):
        return "Other", []

    return ranked[0][0], ranked[0][1]


def _check_severity(description_lower: str) -> list[str]:
    """Return list of severity keywords found in description."""
    found = []
    for kw in SEVERITY_KEYWORDS:
        # Word-boundary match to avoid partial matches
        if re.search(r'\b' + re.escape(kw) + r'\b', description_lower):
            found.append(kw)
    return found


def _build_reason(category: str, matched_keywords: list[str],
                  severity_hits: list[str], description: str) -> str:
    """Build a reason sentence citing specific words from the description."""
    parts = []

    if matched_keywords:
        parts.append(f"Description mentions: {', '.join(repr(k) for k in matched_keywords[:3])}")
    else:
        parts.append("No category keywords matched in description")

    if severity_hits:
        parts.append(f"severity triggered by: {', '.join(repr(s) for s in severity_hits)}")

    return ". ".join(parts) + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle empty descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # Step 1: Match category
    category, matched_keywords = _match_category(description_lower)

    # Step 2: Check severity → determines priority
    severity_hits = _check_severity(description_lower)
    if severity_hits:
        priority = "Urgent"
    elif category == "Other":
        priority = "Standard"
    else:
        priority = "Standard"

    # Step 3: Determine flag
    flag = ""
    if category == "Other" and not matched_keywords:
        flag = "NEEDS_REVIEW"

    # Step 4: Build reason citing description words
    reason = _build_reason(category, matched_keywords, severity_hits, description)

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
    errors = 0
    total = 0
    flagged = 0

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            try:
                result = classify_complaint(row)
                if result["flag"] == "NEEDS_REVIEW":
                    flagged += 1
                results.append(result)
            except Exception as e:
                errors += 1
                print(f"WARNING: Row {total} failed: {e}", file=sys.stderr)
                # Still produce a row with error info
                results.append({
                    "complaint_id": row.get("complaint_id", f"ROW_{total}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    print(f"Processed: {total} rows")
    print(f"Errors:    {errors}")
    print(f"Flagged:   {flagged} (NEEDS_REVIEW)")
    print(f"Output:    {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
