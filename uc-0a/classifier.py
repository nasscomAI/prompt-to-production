"""
UC-0A — Complaint Classifier
Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv

Classifies each citizen complaint into:
  category : Pothole | Flooding | Streetlight | Waste | Noise |
             Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other
  priority : Urgent | Standard | Low
  reason   : One sentence citing words from the description
  flag     : NEEDS_REVIEW (if ambiguous) or blank
"""

import csv
import argparse
import sys
import os

# ── Taxonomy ────────────────────────────────────────────────────────────────

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "fall", "collapse", "collapsed",
    "hospitalised", "hospitalised", "lives at risk", "accident",
    "burns", "stranded", "structural concern",
]

# Each category maps to keywords in priority order.
# The first matching category wins.
CATEGORY_RULES = [
    ("Pothole",         ["pothole", "potholes"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "water"]),
    ("Drain Blockage",  ["drain", "stormwater drain", "drain blocked", "drainage"]),
    ("Streetlight",     ["streetlight", "street light", "lamp", "light", "lighting", "lit", "dark", "sparking"]),
    ("Waste",           ["waste", "garbage", "bins", "overflowing", "litter", "rubbish", "dead animal"]),
    ("Noise",           ["noise", "music", "drilling", "band", "amplifier", "sound", "midnight"]),
    ("Heritage Damage", ["heritage", "historic", "cobblestone", "cobblestones", "tram road",
                          "heritage zone", "ancient", "tagore", "palace", "defaced"]),
    ("Heat Hazard",     ["heat", "temperature", "melting", "hot", "°c", "burns on contact", "sun"]),
    ("Road Damage",     ["road", "tarmac", "surface", "subsidence", "sinking", "cracked",
                          "buckled", "collapsed", "subside", "manhole", "footpath", "pavement"]),
]

# ── Core skill: classify_complaint ──────────────────────────────────────────

def classify_complaint(description: str):
    """
    Analyzes a single complaint description.
    Returns: (category, priority, reason, flag)
    """
    desc_lower = description.lower()

    # Determine priority
    triggered_keyword = next(
        (kw for kw in SEVERITY_KEYWORDS if kw in desc_lower), None
    )
    priority = "Urgent" if triggered_keyword else "Standard"

    # Determine category
    matched_category = None
    matched_keyword = None
    ambiguous = False

    matches = []
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matches.append((category, kw))
                break  # one match per category is enough

    if len(matches) == 0:
        matched_category = "Other"
        ambiguous = True
    elif len(matches) == 1:
        matched_category, matched_keyword = matches[0]
    else:
        # Multiple categories match — take the first (highest-priority) one
        # but flag as NEEDS_REVIEW if two top-level categories clash
        matched_category, matched_keyword = matches[0]
        if matches[0][0] != matches[1][0]:
            ambiguous = True

    # Build reason
    if matched_keyword:
        reason = f"Classified as '{matched_category}' based on '{matched_keyword}' in description."
    else:
        reason = f"No clear category keyword found in description; classified as 'Other'."

    if triggered_keyword:
        reason += f" Priority set to Urgent due to severity keyword: '{triggered_keyword}'."
    else:
        reason += " No severity keywords detected; defaulting to Standard priority."

    flag = "NEEDS_REVIEW" if ambiguous else ""

    return matched_category, priority, reason, flag


# ── Core skill: batch_classify ───────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, classifies every row, writes results CSV.
    Output columns = all original columns + category, priority, reason, flag.
    """
    if not os.path.isfile(input_path):
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    rows_out = []
    fieldnames_out = None

    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        original_fields = reader.fieldnames or []
        fieldnames_out = list(original_fields) + ["category", "priority", "reason", "flag"]

        for row in reader:
            try:
                description = row.get("description", "")
                category, priority, reason, flag = classify_complaint(description)
                row["category"] = category
                row["priority"] = priority
                row["reason"] = reason
                row["flag"] = flag
                rows_out.append(row)
            except Exception as e:
                complaint_id = row.get("complaint_id", "UNKNOWN")
                print(f"WARNING: Skipping row {complaint_id} due to error: {e}", file=sys.stderr)
                continue

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames_out)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Done. {len(rows_out)} rows classified → {output_path}")


# ── CLI entry point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — classify city complaints into predefined categories."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to input CSV (e.g. ../data/city-test-files/test_pune.csv)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to output CSV (e.g. results_pune.csv)"
    )
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
