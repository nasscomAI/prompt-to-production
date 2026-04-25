"""
UC-0A — Complaint Classifier
Built from agents.md (RICE enforcement rules) and skills.md (skill contracts).

Agent role  : Citizen Complaint Classification Agent for Indian municipal corporations.
Agent scope : Classify only — do not generate, modify, or infer descriptions.
"""

import argparse
import csv
import logging
import sys

# ---------------------------------------------------------------------------
# Classification schema — mirrors agents.md enforcement rules exactly
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

# Enforcement rule: priority must be Urgent when any of these appear in description
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ---------------------------------------------------------------------------
# Keyword maps for deterministic category matching
# Order matters: more specific / higher-risk categories are checked first.
# Each entry is (category_name, list_of_trigger_keywords).
# A match on ANY keyword → that category is a candidate.
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = [
    ("Heritage Damage",  ["heritage", "historic", "tram road cobblestone", "heritage street",
                          "heritage lamp", "tagore", "marble palace", "heritage stone",
                          "heritage residential", "heritage precinct", "heritage zone"]),
    ("Flooding",         ["flood", "flooded", "submerged", "waterlog", "inundated",
                          "standing water", "knee-deep", "drain blocked", "water on road",
                          "water logging"]),
    ("Drain Blockage",   ["drain block", "blocked drain", "drain choke", "drain overflow",
                          "drainage", "manhole", "sewer", "sewage"]),
    ("Pothole",          ["pothole", "pot hole", "pothole"]),
    ("Streetlight",      ["streetlight", "street light", "lamp post", "lamp",
                          "lights out", "lighting", "flickering", "sparking", "dark at night",
                          "darkness", "substation"]),
    ("Noise",            ["noise", "music", "loud", "amplifier", "band playing",
                          "playing music", "sound"]),
    ("Road Damage",      ["road surface", "road crack", "cracked", "sinking", "subsided",
                          "road subsid", "buckled", "pothole filling", "footpath broken",
                          "footpath tiles", "pavement", "road damage", "road surface cracked",
                          "tiles broken", "paving", "broken road"]),
    ("Waste",            ["garbage", "waste", "litter", "overflowing bin", "dump",
                          "dumped", "dead animal", "refuse", "trash", "rubbish"]),
    ("Heat Hazard",      ["heat", "hot", "temperature", "heatwave", "heat hazard"]),
]

OUTPUT_FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)


# ---------------------------------------------------------------------------
# Skill 1 — classify_complaint
# Input  : dict with keys complaint_id, date_raised, city, ward, location,
#           description, reported_by, days_open
# Output : dict with keys complaint_id, category, priority, reason, flag
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint row.

    Enforcement rules from agents.md:
    1. Category must be exactly one of the ALLOWED_CATEGORIES.
    2. Priority must be exactly one of: Urgent, Standard, Low.
    3. Priority is Urgent if description contains any SEVERITY_KEYWORDS.
    4. Every output must include a reason sentence citing words from description.
    5. flag = NEEDS_REVIEW when category is genuinely ambiguous (≥2 candidates).
    6. If category cannot be determined → Other + NEEDS_REVIEW.
    7. Single category only — most appropriate one wins.
    8. Deterministic — same input always produces same output.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = row.get("description", "") or ""
    description  = description.strip()

    # --- Error handling: missing / empty description (from skills.md) -------
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Step 1: find all matching category candidates ----------------------
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw.lower() in desc_lower:
                if category not in matched_categories:
                    matched_categories.append(category)
                break  # one keyword match is enough for this category

    # --- Step 2: resolve category and ambiguity flag ------------------------
    if len(matched_categories) == 0:
        category = "Other"
        flag     = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag     = ""
    else:
        # Ambiguous: take the first match (CATEGORY_KEYWORDS is priority-ordered)
        # but flag for human review
        category = matched_categories[0]
        flag     = "NEEDS_REVIEW"

    # --- Step 3: determine priority -----------------------------------------
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)

    if is_urgent:
        priority = "Urgent"
    elif category in ("Flooding", "Heritage Damage", "Drain Blockage", "Heat Hazard"):
        priority = "Standard"
    elif category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # --- Step 4: build reason sentence citing words from description --------
    # Find the first severity keyword hit (if any) for the reason
    triggered_severity = next(
        (kw for kw in SEVERITY_KEYWORDS if kw in desc_lower), None
    )

    # Find the trigger keyword that caused the category match
    triggered_category_kw = None
    for cat, keywords in CATEGORY_KEYWORDS:
        if cat == category:
            for kw in keywords:
                if kw.lower() in desc_lower:
                    triggered_category_kw = kw
                    break
            break

    if triggered_category_kw and triggered_severity:
        reason = (
            f"Description mentions '{triggered_category_kw}' indicating {category}, "
            f"and the word '{triggered_severity}' triggers Urgent priority."
        )
    elif triggered_category_kw:
        reason = (
            f"Description mentions '{triggered_category_kw}', "
            f"classifying this as {category} with {priority} priority."
        )
    elif triggered_severity:
        reason = (
            f"Category set to Other as no clear category keyword found; "
            f"the word '{triggered_severity}' triggers Urgent priority."
        )
    else:
        reason = (
            "No matching category keywords found in the description; "
            "classified as Other and flagged for review."
        )

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ---------------------------------------------------------------------------
# Skill 2 — batch_classify
# Input  : input_path (str), output_path (str)
# Output : CSV file at output_path with columns complaint_id, category,
#          priority, reason, flag
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read the input CSV, classify each row, write results to output CSV.

    Resilience rules from skills.md:
    - If input file is missing → print clear error and exit.
    - If a row is malformed → log warning, classify as Other/Low/NEEDS_REVIEW, continue.
    - Never crash mid-batch; always write partial results.
    - If no rows processed → write empty CSV with headers only.
    """
    # --- Read input ---------------------------------------------------------
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not read input file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Classify each row --------------------------------------------------
    results = []
    for i, row in enumerate(rows, start=2):  # row 1 = header → data starts at line 2
        try:
            result = classify_complaint(row)
        except Exception as exc:
            complaint_id = row.get("complaint_id", f"ROW_{i}")
            logging.warning(
                "Row %d (id=%s) failed classification: %s — defaulting to Other/Low/NEEDS_REVIEW",
                i, complaint_id, exc,
            )
            result = {
                "complaint_id": complaint_id,
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Classification error: {exc}",
                "flag":         "NEEDS_REVIEW",
            }
        results.append(result)

    # --- Write output -------------------------------------------------------
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        print(f"ERROR: Could not write output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Classified {len(results)} complaint(s). Results written to: {output_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Citizen Complaint Classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
  python classifier.py --input ../data/city-test-files/test_kolkata.csv --output results_kolkata.csv
        """,
    )
    parser.add_argument(
        "--input",  required=True,
        help="Path to test_[city].csv (e.g., ../data/city-test-files/test_pune.csv)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write results CSV (e.g., results_pune.csv)"
    )
    args = parser.parse_args()
    batch_classify(args.input, args.output)
