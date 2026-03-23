"""
UC-0A — Complaint Classifier
Built per: agents.md (role, intent, context, enforcement) + skills.md (classify_complaint, batch_classify)
"""
import argparse
import csv
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ── agents.md → enforcement ──────────────────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# agents.md: "Priority must be Urgent if description contains any of these severity keywords"
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# agents.md: Category must be exactly one of the allowed values — no variations/sub-categories
# Each key maps to a list of (keyword, cited_phrase) tuples.
# cited_phrase is what gets surfaced verbatim in the reason field.
CATEGORY_KEYWORD_MAP = {
    "Pothole":          ["pothole"],
    "Flooding":         ["flood", "flooded", "flooding", "submerged", "waterlogging"],
    "Streetlight":      ["streetlight", "street light", "lamp", "dark", "spark", "electrical"],
    "Waste":            ["waste", "garbage", "trash", "dumped", "smell", "stench", "dead animal"],
    "Noise":            ["noise", "loud", "music", "blaring", "honking"],
    "Road Damage":      ["road damage", "crack", "sinkhole", "sink hole", "broken tile",
                         "footpath", "pavement", "uneven road"],
    "Heritage Damage":  ["heritage", "monument", "historical", "ancient"],
    "Heat Hazard":      ["heat", "hot surface", "overheating", "thermal"],
    "Drain Blockage":   ["drain", "sewer", "manhole", "clogged", "overflow"],
}


# ── skill: classify_complaint ─────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    skills.md → classify_complaint
    Input : a single dict row with at minimum a 'description' key.
    Output: dict with complaint_id, category, priority, reason, flag.

    Enforcement (agents.md):
    - Category: exactly one of ALLOWED_CATEGORIES.
    - Priority: Urgent iff any SEVERITY_KEYWORD is present; else Standard or Low.
    - Reason: exactly one sentence citing specific words from the description.
    - Ambiguous → category: Other, flag: NEEDS_REVIEW.
    """
    description = row.get("description", "").strip()
    desc_lower  = description.lower()

    # ── 1. Priority (agents.md enforcement) ──────────────────────────────────
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_severity:
        priority = "Urgent"
    elif description:
        priority = "Standard"
    else:
        priority = "Low"           # empty / blank description

    # ── 2. Category (agents.md enforcement — no hallucinated sub-categories) ──
    matched_categories = []
    first_matched_keyword = {}

    for cat, keywords in CATEGORY_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                first_matched_keyword[cat] = kw
                break                           # one match per category is enough

    flag = "None"

    # agents.md: "cannot be confidently determined → Other + NEEDS_REVIEW"
    if not matched_categories:
        category = "Other"
        flag     = "NEEDS_REVIEW"
        reason   = (
            f"The description provides insufficient identifying keywords to assign a "
            f"confident category, so it is classified as Other with {priority} priority."
        )

    elif len(matched_categories) > 1:
        # Genuinely ambiguous — multiple category signals in one description
        category = "Other"
        flag     = "NEEDS_REVIEW"
        kw_list  = "', '".join(first_matched_keyword[c] for c in matched_categories[:2])
        reason   = (
            f"The description contains conflicting signals — keywords '{kw_list}' "
            f"match multiple categories — so it is flagged for review with {priority} priority."
        )

    else:
        category = matched_categories[0]
        kw       = first_matched_keyword[category]

        # Build severity citation if Urgent
        if matched_severity:
            severity_cite = f" and mentions '{matched_severity[0]}' triggering Urgent priority"
        else:
            severity_cite = f" and is assigned {priority} priority as no severity keywords appear"

        reason = (
            f"Classified as {category} because the description contains '{kw}'"
            f"{severity_cite}."
        )

    # ── 3. Final safety-check: category must be in the allowed list ───────────
    assert category in ALLOWED_CATEGORIES, f"BUG: '{category}' not in ALLOWED_CATEGORIES"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── skill: batch_classify ─────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str) -> None:
    """
    skills.md → batch_classify
    Input : path to test_[city].csv
    Output: results CSV written to output_path with category, priority, reason, flag appended.

    Error handling (skills.md):
    - Malformed rows → log error, set NEEDS_REVIEW, continue.
    - Output written even if some rows fail.
    - Rows are classified independently (no cross-row inference).
    """
    results   = []
    out_fields = None

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader    = csv.DictReader(infile)
        in_fields = list(reader.fieldnames or [])

        # Determine output column order: preserve original columns, append classification cols
        classification_cols = ["category", "priority", "reason", "flag"]
        out_fields = in_fields + [c for c in classification_cols if c not in in_fields]

        for row in reader:
            # skills.md constraint: process every row independently
            try:
                if not any(v and v.strip() for v in row.values()):
                    raise ValueError("Entirely empty row — skipping.")

                result = classify_complaint(row)

                row["category"] = result["category"]
                row["priority"] = result["priority"]
                row["reason"]   = result["reason"]
                row["flag"]     = result["flag"]

            except Exception as exc:
                # skills.md error_handling: log, NEEDS_REVIEW, continue
                logging.error("Row %s failed: %s", row.get("complaint_id", "?"), exc)
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"]   = (
                    f"Row could not be processed due to an unexpected error; "
                    f"manual review required."
                )
                row["flag"] = "NEEDS_REVIEW"

            results.append(row)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    logging.info("Done. %d rows written to %s", len(results), output_path)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")