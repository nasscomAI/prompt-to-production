#!/usr/bin/env python3
"""
app.py — UC-0A Complaint Classifier

Implements the two skills defined in skills.md (classify_complaint,
batch_classify) under the enforcement rules defined in agents.md.

Usage (per UC README run command):
    python app.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import os
import re
import sys

# ---------------------------------------------------------------------------
# Fixed schema (agents.md enforcement: exact strings only, no variations)
# ---------------------------------------------------------------------------

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

FLAG_VALUES = {"NEEDS_REVIEW", ""}

# Severity keywords that must trigger Urgent (agents.md enforcement)
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

# Keyword sets used to deterministically (and therefore consistently,
# avoiding taxonomy drift) map description text to an allowed category.
# Order matters only for tie-break reporting; ambiguity is detected when
# more than one category's keywords match.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "pot hole"],
    "Flooding": ["flood", "flooding", "flooded", "waterlogged", "waterlogging"],
    "Streetlight": ["streetlight", "street light", "streetlamp", "street lamp", "lamp post", "lamppost"],
    "Waste": ["garbage", "trash", "waste", "litter", "dumping", "dump"],
    "Noise": ["noise", "loud", "noisy", "honking", "music blaring"],
    "Road Damage": ["road damage", "cracked road", "broken road", "road crack", "damaged road"],
    "Heritage Damage": ["heritage", "monument", "historic", "historical structure"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "extreme heat", "sunstroke"],
    "Drain Blockage": ["drain", "drainage", "sewer", "clogged", "blocked drain"],
}

DESCRIPTION_FIELD_CANDIDATES = ["description", "complaint", "complaint_description", "text"]


def _find_description_field(row):
    """Locate the description column name from known candidates."""
    for candidate in DESCRIPTION_FIELD_CANDIDATES:
        if candidate in row:
            return candidate
    return None


def _find_keyword_matches(text_lower, keywords):
    """Return list of keywords found in text_lower."""
    found = []
    for kw in keywords:
        # word/phrase boundary match, case-insensitive (text already lowered)
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower):
            found.append(kw)
    return found


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row):
    """
    Classify a single complaint row.

    Input: dict representing one CSV row (must contain a description field).
    Output: dict with keys category, priority, reason, flag.

    Error handling (skills.md):
      - missing/empty description -> Other / Low / explanatory reason / NEEDS_REVIEW
      - severity keyword present -> priority forced Urgent regardless of category
      - ambiguous / no clear category match -> closest category (or Other) + NEEDS_REVIEW
      - reason always populated, always cites evidence (or states uncertainty)
      - category always coerced into the allowed list, never invented
    """
    desc_field = _find_description_field(row)
    description = (row.get(desc_field) or "").strip() if desc_field else ""

    # --- Missing/empty description ---
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description was provided for this complaint, so it cannot be classified with confidence.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # --- Category matching ---
    matches = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        found = _find_keyword_matches(description_lower, keywords)
        if found:
            matches[category] = found

    flag = ""
    if len(matches) == 1:
        category = next(iter(matches))
        matched_words = matches[category]
        reason_evidence = ", ".join(f"'{w}'" for w in matched_words)
        reason = f"Classified as {category} because the description mentions {reason_evidence}."
    elif len(matches) > 1:
        # Genuinely ambiguous: more than one category plausible.
        # Do not guess confidently — pick the category with the most
        # specific/longest keyword match as the closest fit, but flag it.
        category = max(matches, key=lambda c: max(len(w) for w in matches[c]))
        matched_words = matches[category]
        reason_evidence = ", ".join(f"'{w}'" for w in matched_words)
        other_cats = ", ".join(c for c in matches if c != category)
        reason = (
            f"Description contains indicators for multiple categories "
            f"(matched {reason_evidence} for {category}, also overlaps with {other_cats}); "
            f"flagged for review rather than confidently classified."
        )
        flag = "NEEDS_REVIEW"
    else:
        # No keyword match at all — do not hallucinate a sub-category.
        category = "Other"
        reason = (
            "No specific words in the description matched a known category, "
            "so this complaint could not be confidently classified."
        )
        flag = "NEEDS_REVIEW"

    # --- Safety net: category must always be in the allowed list ---
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classification result was invalid and has been reset to Other pending review."

    # --- Priority / severity keyword check (overrides everything) ---
    severity_found = _find_keyword_matches(description_lower, SEVERITY_KEYWORDS)
    if severity_found:
        priority = "Urgent"
        sev_evidence = ", ".join(f"'{w}'" for w in severity_found)
        reason = (
            f"{reason} Marked Urgent due to severity keyword(s) {sev_evidence} in the description."
        )
    else:
        # No severity keywords: Standard by default, Low only for minor/no-match cases.
        if category == "Other" and not matches:
            priority = "Low"
        else:
            priority = "Standard"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    if flag not in FLAG_VALUES:
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path, output_path):
    """
    Read the input CSV, classify every row via classify_complaint, and
    write the output CSV with category/priority/reason/flag added.

    Error handling (skills.md):
      - input file missing/unreadable -> halt, no partial/empty output written
      - malformed row -> still emitted, coerced to Other/Low/NEEDS_REVIEW
        with an explanatory reason, never dropped
      - every input row produces exactly one output row
      - invalid category returned by classify_complaint is coerced to Other
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
    except Exception as exc:
        raise IOError(f"Could not read input file '{input_path}': {exc}")

    output_fieldnames = list(fieldnames)
    for extra in ("category", "priority", "reason", "flag"):
        if extra not in output_fieldnames:
            output_fieldnames.append(extra)

    output_rows = []
    for row in rows:
        try:
            result = classify_complaint(row)

            # Final enforcement check: never let an invalid category through.
            if result.get("category") not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"
                result["reason"] = (
                    "Classifier produced an invalid category; coerced to Other pending review."
                )
            if result.get("priority") not in ALLOWED_PRIORITIES:
                result["priority"] = "Standard"
            if not result.get("reason"):
                result["reason"] = "No justification was generated; flagged for review."
                result["flag"] = "NEEDS_REVIEW"
            if result.get("flag") not in FLAG_VALUES:
                result["flag"] = "NEEDS_REVIEW"

        except Exception as exc:
            # Malformed row: never drop it — emit a safe fallback row.
            result = {
                "category": "Other",
                "priority": "Low",
                "reason": f"Row could not be processed due to an error ({exc}); flagged for review.",
                "flag": "NEEDS_REVIEW",
            }

        merged = dict(row)
        merged.update(result)
        output_rows.append(merged)

    # Every input row must produce exactly one output row.
    assert len(output_rows) == len(rows), "Row count mismatch: rows were dropped or duplicated."

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            for row in output_rows:
                writer.writerow(row)
    except Exception as exc:
        raise IOError(f"Could not write output file '{output_path}': {exc}")

    return output_path


# ---------------------------------------------------------------------------
# CLI entry point (matches UC README run command)
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)
    except IOError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)

    print(f"Classification complete. Output written to: {args.output}")


if __name__ == "__main__":
    main()