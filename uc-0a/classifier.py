"""
UC-0A — Complaint Classifier
Classifies citizen complaints into category, priority, reason, and flag.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# ── Enforcement: Fixed taxonomy (agents.md rule 1) ──────────────────────────
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

# ── Enforcement: Severity keywords that force Urgent (agents.md rule 3) ─────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

# ── Category keyword mapping ────────────────────────────────────────────────
# Each category has a list of (keyword/phrase, weight) tuples.
# We score each category and pick the highest. Ties or low scores → NEEDS_REVIEW.
CATEGORY_RULES = {
    "Pothole": [
        ("pothole", 10),
        ("tyre damage", 3),
        ("tire damage", 3),
    ],
    "Flooding": [
        ("flood", 10),
        ("flooded", 10),
        ("waterlog", 8),
        ("water-log", 8),
        ("knee-deep", 5),
        ("submerge", 5),
        ("stranded", 3),
        ("inundated", 5),
    ],
    "Streetlight": [
        ("streetlight", 10),
        ("street light", 10),
        ("lights out", 7),
        ("light out", 7),
        ("flickering", 5),
        ("sparking", 5),
        ("dark at night", 5),
        ("lamp post", 5),
        ("no lighting", 5),
    ],
    "Waste": [
        ("garbage", 10),
        ("waste", 8),
        ("rubbish", 8),
        ("trash", 8),
        ("overflowing bin", 8),
        ("dumped", 6),
        ("dead animal", 8),
        ("litter", 5),
        ("debris", 4),
        ("smell", 3),
    ],
    "Noise": [
        ("noise", 10),
        ("loud music", 8),
        ("music past midnight", 10),
        ("playing music", 8),
        ("honking", 6),
        ("loudspeaker", 8),
        ("decibel", 5),
    ],
    "Road Damage": [
        ("road surface cracked", 10),
        ("road.*crack", 8),
        ("sinking", 6),
        ("footpath.*broken", 8),
        ("manhole cover missing", 8),
        ("pothole", 0),  # pothole has its own category — handled separately
        ("upturned", 4),
        ("road damage", 10),
        ("tiles broken", 5),
    ],
    "Heritage Damage": [
        ("heritage", 10),
        ("monument", 8),
        ("historical", 6),
        ("protected structure", 8),
        ("ancient", 5),
    ],
    "Heat Hazard": [
        ("heat", 8),
        ("heatstroke", 10),
        ("heat hazard", 10),
        ("sunstroke", 8),
        ("extreme temperature", 6),
        ("heat wave", 8),
    ],
    "Drain Blockage": [
        ("drain block", 10),
        ("blocked drain", 10),
        ("clogged drain", 10),
        ("drainage", 6),
        ("sewage", 6),
        ("manhole overflow", 6),
        ("gutter block", 6),
        ("nala block", 6),
    ],
}


def _score_category(description_lower: str) -> list[tuple[str, int, list[str]]]:
    """
    Score every category against the description.
    Returns list of (category, score, matched_keywords) sorted desc by score.
    """
    scores = []
    for category, patterns in CATEGORY_RULES.items():
        total = 0
        matched = []
        for pattern, weight in patterns:
            if weight == 0:
                continue
            # Use regex search for patterns containing regex meta-chars
            if any(c in pattern for c in ".*+?[]()"):
                if re.search(pattern, description_lower):
                    total += weight
                    matched.append(pattern)
            else:
                if pattern in description_lower:
                    total += weight
                    matched.append(pattern)
        scores.append((category, total, matched))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def _check_severity(description_lower: str) -> tuple[bool, list[str]]:
    """
    Check if description contains severity keywords.
    Returns (is_urgent, list_of_found_keywords).
    """
    found = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
    return (len(found) > 0, found)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules from agents.md:
    - Category must be from ALLOWED_CATEGORIES exactly
    - Priority is Urgent if severity keywords present
    - Reason must cite specific words from description
    - Ambiguous cases get NEEDS_REVIEW flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty/missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty or missing description.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower().strip()

    # ── Step 1: Score categories ──────────────────────────────────────────
    scores = _score_category(desc_lower)
    top = scores[0]
    runner_up = scores[1] if len(scores) > 1 else ("", 0, [])

    # Determine category and flag
    if top[1] == 0:
        # No category matched at all
        category = "Other"
        flag = "NEEDS_REVIEW"
        match_reason = "no category keywords matched"
    elif top[1] > 0 and runner_up[1] > 0 and (top[1] - runner_up[1]) <= 3:
        # Close scores — ambiguous but pick the top one and flag
        category = top[0]
        flag = "NEEDS_REVIEW"
        match_reason = f"matched '{', '.join(top[2])}' but also close to {runner_up[0]}"
    else:
        category = top[0]
        flag = ""
        match_reason = f"matched '{', '.join(top[2])}'"

    # ── Step 2: Check for special cases ───────────────────────────────────

    # Heritage street with lights out → Heritage Damage (heritage is primary context)
    if "heritage" in desc_lower and category == "Streetlight":
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
        match_reason = "heritage site with streetlight issue — classified as Heritage Damage"

    # Drain blocked causing flooding → Drain Blockage is the root cause
    if "drain" in desc_lower and "block" in desc_lower and category == "Flooding":
        category = "Drain Blockage"
        flag = "NEEDS_REVIEW"
        match_reason = "drain blockage causing flooding — root cause is drain"

    # ── Step 3: Determine priority ────────────────────────────────────────
    is_urgent, severity_words = _check_severity(desc_lower)
    if is_urgent:
        priority = "Urgent"
    elif row.get("days_open", ""):
        # Use days_open as a secondary signal only — not for severity
        priority = "Standard"
    else:
        priority = "Standard"

    # ── Step 4: Build reason citing description words ─────────────────────
    # Extract a short quote from description for the reason
    desc_short = description[:80].rstrip()
    if len(description) > 80:
        desc_short += "..."

    if is_urgent:
        reason = (
            f"Classified as {category} because description contains {match_reason}. "
            f"Priority Urgent due to severity keyword(s): {', '.join(severity_words)}. "
            f"Description: \"{desc_short}\""
        )
    else:
        reason = (
            f"Classified as {category} because description contains {match_reason}. "
            f"Description: \"{desc_short}\""
        )

    # ── Final validation: category must be in allowed list ────────────────
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

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

    - Flags nulls and bad rows without crashing.
    - Produces output even if some rows fail.
    - Prints a summary to stdout.
    """
    # Read input
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}")
        sys.exit(1)

    if not rows:
        print("WARNING: Input file contains no data rows.")
        sys.exit(1)

    # Classify each row
    results = []
    category_counts: dict[str, int] = {}
    urgent_count = 0
    flagged_count = 0

    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", f"ROW_{i+1}"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {e}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

        # Track stats
        cat = result["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            flagged_count += 1

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    print(f"\n{'='*60}")
    print(f"  UC-0A Classification Summary — {input_path}")
    print(f"{'='*60}")
    print(f"  Total rows processed: {len(results)}")
    print(f"  Urgent priority:      {urgent_count}")
    print(f"  Flagged NEEDS_REVIEW: {flagged_count}")
    print(f"\n  Category breakdown:")
    for cat in ALLOWED_CATEGORIES:
        count = category_counts.get(cat, 0)
        if count > 0:
            print(f"    {cat:20s}: {count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
