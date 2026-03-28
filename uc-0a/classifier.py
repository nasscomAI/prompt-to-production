"""
UC-0A — Complaint Classifier
Built using agents.md (RICE framework) and skills.md enforcement rules.

Classification Schema (from agents.md enforcement):
  - category: Pothole | Flooding | Streetlight | Waste | Noise |
               Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other
  - priority: Urgent | Standard | Low
  - reason:   One sentence citing specific words from the description
  - flag:     NEEDS_REVIEW or blank
"""
import argparse
import csv
import re
import sys
import os

# ──────────────────────────────────────────────────────────────────────
# Constants — derived from agents.md enforcement rules
# ──────────────────────────────────────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword-to-category mapping — order matters (more specific patterns first)
# Each entry: (list of keywords/phrases, category)
CATEGORY_RULES = [
    # Heritage Damage — must come before Road Damage / Streetlight
    (["heritage", "monument", "historical", "ancient structure"], "Heritage Damage"),

    # Heat Hazard
    (["heat", "sunstroke", "heatwave", "high temperature", "scorching"], "Heat Hazard"),

    # Drain Blockage — must come before Flooding
    (["drain block", "drain clog", "blocked drain", "clogged drain",
      "choked drain", "drain choke", "manhole", "sewer block", "sewer clog",
      "gutter block"], "Drain Blockage"),

    # Flooding
    (["flood", "waterlog", "water-log", "submerge", "inundat",
      "knee-deep", "waist-deep", "stranded", "water logging",
      "standing in water"], "Flooding"),

    # Pothole
    (["pothole", "pot hole", "pot-hole", "crater in road",
      "tyre damage", "tire damage"], "Pothole"),

    # Streetlight
    (["streetlight", "street light", "street-light", "lamp post",
      "lamppost", "light out", "lights out", "flickering",
      "sparking", "dark at night", "no light"], "Streetlight"),

    # Waste
    (["garbage", "waste", "rubbish", "trash", "litter",
      "overflowing bin", "overflow", "dump", "dead animal",
      "carcass", "stink", "smell", "debris"], "Waste"),

    # Noise
    (["noise", "loud music", "music past midnight", "honking",
      "blaring", "sound pollution", "noise pollution",
      "loudspeaker", "loud speaker", "dj ", "midnight"], "Noise"),

    # Road Damage (general — after Pothole)
    (["road crack", "road surface crack", "sinking road", "road sinking",
      "broken road", "road broken", "road damage", "footpath",
      "pavement broken", "tiles broken", "upturned", "road cave",
      "bitumen peel", "asphalt damage", "road subsid"], "Road Damage"),
]


def _contains_severity_keyword(text: str) -> list[str]:
    """Return list of severity keywords found in text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in text_lower]


def _match_category(description: str) -> tuple[str, list[str], bool]:
    """
    Match description to a category using keyword rules.

    Returns:
        (category, matched_keywords, is_ambiguous)
    """
    desc_lower = description.lower()
    matches = []  # list of (category, matched_keywords)

    for keywords, category in CATEGORY_RULES:
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            matches.append((category, matched))

    if len(matches) == 0:
        return "Other", [], True
    elif len(matches) == 1:
        return matches[0][0], matches[0][1], False
    else:
        # Multiple categories matched — check if truly ambiguous
        categories_found = list(set(m[0] for m in matches))
        if len(categories_found) == 1:
            # Same category through different keyword groups
            all_keywords = []
            for _, kws in matches:
                all_keywords.extend(kws)
            return categories_found[0], all_keywords, False
        else:
            # Genuinely ambiguous — pick the first (highest priority) match
            # but flag for review
            all_keywords = []
            for _, kws in matches:
                all_keywords.extend(kws)
            return matches[0][0], all_keywords, True


def _determine_priority(description: str, severity_hits: list[str], category: str) -> str:
    """
    Determine priority per agents.md enforcement:
    - Urgent if ANY severity keyword present
    - Standard for infrastructure impact or active disruption
    - Low for cosmetic or non-blocking issues
    """
    if severity_hits:
        return "Urgent"

    # Standard indicators — active disruption / infrastructure impact
    standard_indicators = [
        "damage", "broken", "blocked", "flooded", "stranded", "dark",
        "dangerous", "risk", "safety", "overflowing", "cracked",
        "sinking", "missing", "not removed", "inaccessible",
        "health concern", "affecting", "vehicles affected"
    ]
    desc_lower = description.lower()
    for indicator in standard_indicators:
        if indicator in desc_lower:
            return "Standard"

    # Categories that are inherently infrastructure / disruption
    if category in ["Pothole", "Flooding", "Drain Blockage", "Road Damage",
                     "Heritage Damage", "Heat Hazard"]:
        return "Standard"

    return "Low"


def _build_reason(description: str, category: str, priority: str,
                  matched_keywords: list[str], severity_hits: list[str]) -> str:
    """
    Build a reason sentence that cites specific words from the description.
    Per agents.md: must cite specific words/phrases directly from the complaint.
    """
    # Extract a short quoted phrase from the description for citation
    # Pick the most relevant substring (up to ~60 chars around the first keyword match)
    desc_lower = description.lower()
    cited_phrase = ""

    for kw in matched_keywords:
        idx = desc_lower.find(kw)
        if idx != -1:
            # Extract surrounding context (up to 80 chars centered on keyword)
            start = max(0, idx - 10)
            end = min(len(description), idx + len(kw) + 40)
            cited_phrase = description[start:end].strip()
            break

    if not cited_phrase and description:
        cited_phrase = description[:60].strip()

    # Build the reason
    if severity_hits:
        severity_citation = ", ".join(f'"{kw}"' for kw in severity_hits)
        reason = (f'Classified as {category} ({priority}) because description mentions '
                  f'"{cited_phrase}" and contains severity keyword(s) {severity_citation}.')
    else:
        reason = (f'Classified as {category} ({priority}) because description mentions '
                  f'"{cited_phrase}".')

    return reason


# ──────────────────────────────────────────────────────────────────────
# Skill 1: classify_complaint
# ──────────────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict with at minimum a 'description' field.
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Implements all enforcement rules from agents.md:
      1. Category is exactly one of the 10 allowed values
      2. Priority is Urgent if severity keywords present
      3. Reason cites specific words from the description
      4. Flag is NEEDS_REVIEW only for genuinely ambiguous complaints
      5. No hallucinated sub-categories
      6. Exactly four classification fields per row
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Error handling (from skills.md): missing or empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided — unable to classify.",
            "flag": "NEEDS_REVIEW"
        }

    # Step 1: Detect severity keywords
    severity_hits = _contains_severity_keyword(description)

    # Step 2: Match category
    category, matched_keywords, is_ambiguous = _match_category(description)

    # Step 3: Determine priority
    priority = _determine_priority(description, severity_hits, category)

    # Step 4: Set flag
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    # Step 5: Build reason citing specific words from description
    reason = _build_reason(description, category, priority,
                           matched_keywords, severity_hits)

    # Enforcement validation: category must be in allowed list
    assert category in ALLOWED_CATEGORIES, f"Invalid category: {category}"
    assert priority in ("Urgent", "Standard", "Low"), f"Invalid priority: {priority}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


# ──────────────────────────────────────────────────────────────────────
# Skill 2: batch_classify
# ──────────────────────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Input:  input_path — CSV with complaint rows
            output_path — path for classified output CSV
    Output: CSV with original columns + category, priority, reason, flag

    Implements skills.md error_handling:
      - Invalid/missing input file --> clear error and exit
      - Individual row failures --> classify as Other/NEEDS_REVIEW, continue
      - Never silently skip rows
      - Logs summary at end
    """
    # Validate input file exists
    if not os.path.isfile(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    # Read input CSV
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print(f"ERROR: Input file is not a valid CSV or is empty: {input_path}")
                sys.exit(1)
            input_fieldnames = list(reader.fieldnames)
            rows = list(reader)
    except Exception as e:
        print(f"ERROR: Failed to read input CSV '{input_path}': {e}")
        sys.exit(1)

    if not rows:
        print(f"WARNING: Input file has no data rows: {input_path}")

    # Classification columns to append
    classification_fields = ["category", "priority", "reason", "flag"]
    output_fieldnames = input_fieldnames + classification_fields

    # Counters for summary
    total = len(rows)
    successful = 0
    needs_review = 0
    failed = 0

    results = []

    for i, row in enumerate(rows, start=1):
        try:
            classification = classify_complaint(row)

            # Merge original row with classification output
            output_row = dict(row)
            output_row["category"] = classification["category"]
            output_row["priority"] = classification["priority"]
            output_row["reason"] = classification["reason"]
            output_row["flag"] = classification["flag"]

            results.append(output_row)

            if classification["flag"] == "NEEDS_REVIEW":
                needs_review += 1
            successful += 1

            print(f"  Row {i}/{total}: {classification['complaint_id']} --> "
                  f"{classification['category']} | {classification['priority']}"
                  f"{' | NEEDS_REVIEW' if classification['flag'] else ''}")

        except Exception as e:
            # Error handling: classify failed rows but don't skip them
            failed += 1
            complaint_id = row.get("complaint_id", f"row_{i}")
            print(f"  Row {i}/{total}: {complaint_id} --> CLASSIFICATION FAILED: {e}")

            output_row = dict(row)
            output_row["category"] = "Other"
            output_row["priority"] = "Standard"
            output_row["reason"] = f"Classification failed — {str(e)}"
            output_row["flag"] = "NEEDS_REVIEW"
            results.append(output_row)
            needs_review += 1

    # Write output CSV
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Failed to write output CSV '{output_path}': {e}")
        sys.exit(1)

    # Log summary (per skills.md requirement)
    print(f"\n{'='*60}")
    print(f"  Classification Summary")
    print(f"{'='*60}")
    print(f"  Total rows processed : {total}")
    print(f"  Successful           : {successful}")
    print(f"  Failed (fallback)    : {failed}")
    print(f"  Flagged NEEDS_REVIEW : {needs_review}")
    print(f"  Output written to    : {output_path}")
    print(f"{'='*60}")


# ──────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    print(f"Classifying complaints from: {args.input}")
    print(f"Writing results to: {args.output}\n")

    batch_classify(args.input, args.output)
    print(f"\nDone. Results written to {args.output}")
