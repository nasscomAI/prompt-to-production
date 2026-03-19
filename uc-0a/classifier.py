"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md enforcement rules.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv
import sys

# -------------------------------------------------------------------
# Schema — enforcement from agents.md / README.md
# -------------------------------------------------------------------

ALLOWED_CATEGORIES = {
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
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
}

# Keyword → category mapping (checked in order; first match wins)
CATEGORY_RULES = [
    ({"pothole"},                              "Pothole"),
    ({"flood", "flooded", "flooding",
      "waterlog", "inundated", "knee-deep"},  "Flooding"),
    ({"streetlight", "street light",
      "lamp", "light out", "lights out",
      "sparking", "flickering"},              "Streetlight"),
    ({"garbage", "waste", "rubbish",
      "overflowing bin", "dead animal",
      "dumped"},                              "Waste"),
    ({"noise", "music", "sound",
      "loud", "midnight"},                    "Noise"),
    ({"road", "pothole", "cracked",
      "sinking", "manhole", "footpath",
      "tiles", "upturned", "broken"},        "Road Damage"),
    ({"heritage", "historic"},               "Heritage Damage"),
    ({"heat", "temperature", "hot"},         "Heat Hazard"),
    ({"drain", "drainage", "blocked drain",
      "drain blocked"},                      "Drain Blockage"),
]


# -------------------------------------------------------------------
# Skill: classify_complaint
# -------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md):
    1. category must be exactly one of the ALLOWED_CATEGORIES
    2. priority = Urgent if any SEVERITY_KEYWORD appears in description
    3. reason must cite specific words from the description
    4. flag = NEEDS_REVIEW if category cannot be determined confidently
    5. Taxonomy must not drift — always exact strings from ALLOWED_CATEGORIES
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    # --- Handle missing / empty description ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description was empty or unreadable.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Determine category ---
    category = None
    matched_keyword = None
    for keywords, cat in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keyword = kw
                break
        if category:
            break

    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Final safety check — must be in allowed set
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # --- Determine priority ---
    triggered_keyword = next(
        (kw for kw in SEVERITY_KEYWORDS if kw in desc_lower), None
    )
    priority = "Urgent" if triggered_keyword else "Standard"

    # Downgrade to Low only for noise / minor nuisance with no severity keywords
    if category == "Noise" and not triggered_keyword:
        priority = "Low"

    # --- Build reason (must cite specific words from description) ---
    if flag == "NEEDS_REVIEW":
        reason = (
            f"Could not confidently determine category from description: "
            f'"{description[:80]}{"..." if len(description) > 80 else ""}"'
        )
    elif triggered_keyword:
        reason = (
            f'Classified as {category} based on "{matched_keyword}" in description; '
            f'priority set to Urgent due to severity keyword "{triggered_keyword}".'
        )
    else:
        reason = (
            f'Classified as {category} based on "{matched_keyword}" in description.'
        )

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# -------------------------------------------------------------------
# Skill: batch_classify
# -------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    - Flags nulls and bad rows with NEEDS_REVIEW instead of crashing
    - Produces output even if some rows fail
    """
    output_fields = [
        "complaint_id", "date_raised", "city", "ward",
        "location", "description", "reported_by", "days_open",
        "category", "priority", "reason", "flag",
    ]

    results = []
    errors  = 0

    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    # Merge original row + classification fields
                    out_row = {
                        "complaint_id": row.get("complaint_id", ""),
                        "date_raised":  row.get("date_raised", ""),
                        "city":         row.get("city", ""),
                        "ward":         row.get("ward", ""),
                        "location":     row.get("location", ""),
                        "description":  row.get("description", ""),
                        "reported_by":  row.get("reported_by", ""),
                        "days_open":    row.get("days_open", ""),
                        "category":     classification["category"],
                        "priority":     classification["priority"],
                        "reason":       classification["reason"],
                        "flag":         classification["flag"],
                    }
                    results.append(out_row)
                except Exception as e:
                    errors += 1
                    print(
                        f"[WARN] Row {row.get('complaint_id', '?')} failed: {e}",
                        file=sys.stderr
                    )
                    # Still write the row — mark as NEEDS_REVIEW
                    results.append({
                        **{k: row.get(k, "") for k in output_fields[:8]},
                        "category": "Other",
                        "priority": "Low",
                        "reason":   f"Processing error: {e}",
                        "flag":     "NEEDS_REVIEW",
                    })

    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows ({errors} with errors).")


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
