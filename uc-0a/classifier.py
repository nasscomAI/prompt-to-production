"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify skills per agents.md RICE rules.
"""
import argparse
import csv
import sys

# ── Taxonomy (agents.md context) ──────────────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Ordered by specificity — first match wins
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole", "pot hole", "pot-hole"]),
    ("Drain Blockage",  ["drain block", "blocked drain", "drain chok", "gutter block",
                         "sewer block", "drain overflow", "drain clog"]),
    ("Flooding",        ["flood", "waterlog", "waterlogged", "submerged", "inundated",
                         "knee-deep", "standing water", "knee deep"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "lamppost",
                         "light out", "no light", "lights not working", "dark road",
                         "street lamp", "bulb fused", "bulb gone"]),
    ("Waste",           ["garbage", "waste", "rubbish", "litter", "trash",
                         "dumping", "municipal waste", "overflowing bin", "sewage smell",
                         "sanitation"]),
    ("Noise",           ["noise", "loud", "blaring", "honking", "sound pollution",
                         "nuisance sound", "music blasting"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "ancient building",
                         "protected structure", "heritage site"]),
    ("Heat Hazard",     ["heat hazard", "heat stroke", "extreme heat", "heat wave",
                         "heatwave", "heat island", "overheating"]),
    ("Road Damage",     ["road damage", "road crack", "road broken", "pavement crack",
                         "tarmac", "road surface", "road collapsed", "road caved"]),
]

# agents.md enforcement rule 2 — severity keywords → Urgent
URGENT_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "fallen", "collapse", "collapsed",
]


# ── Skill: classify_complaint ─────────────────────────────────────────────────
def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: category, priority, reason, flag.
    Enforcement rules from agents.md are applied explicitly in this function.
    """
    description = row.get("description", "").strip()

    # Error case: missing or empty description
    if not description:
        return {
            "category": "Other",
            "priority":  "Low",
            "reason":    "No description provided — cannot classify.",
            "flag":      "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Rule 1: category — first keyword match wins ───────────────────────────
    matched_category = None
    matched_keywords: list[str] = []

    for category, keywords in CATEGORY_KEYWORDS:
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            matched_category = category
            matched_keywords = hits
            break

    # Ambiguity: no keyword matched → Other + NEEDS_REVIEW (Rule 4)
    if matched_category is None:
        return {
            "category": "Other",
            "priority":  _priority(desc_lower, []),
            "reason":    f"No recognised category keyword found in: '{description[:80]}'.",
            "flag":      "NEEDS_REVIEW",
        }

    # ── Rule 2: priority — check severity keywords ────────────────────────────
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if urgent_hits else "Standard"

    # ── Rule 3: reason — must cite specific words from description ────────────
    reason_parts = [f"'{kw}'" for kw in matched_keywords[:2]]
    reason = f"Description contains {', '.join(reason_parts)}, indicating {matched_category}."
    if urgent_hits:
        urgent_parts = [f"'{kw}'" for kw in urgent_hits[:2]]
        reason += f" Severity keyword(s) {', '.join(urgent_parts)} found — priority set to Urgent."

    return {
        "category": matched_category,
        "priority":  priority,
        "reason":    reason,
        "flag":      "",
    }


def _priority(desc_lower: str, _: list) -> str:
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    return "Urgent" if urgent_hits else "Standard"


# ── Skill: batch_classify ─────────────────────────────────────────────────────
def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, classify each row, write results CSV.
    Returns summary: {total, urgent, needs_review, errors}.
    Aborts (does not write output) if file or required column is missing.
    Never crashes the batch on a single bad row.
    """
    # Validate input file exists and has required column
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "description" not in (reader.fieldnames or []):
                sys.exit(
                    f"ERROR: Input file '{input_path}' has no 'description' column. "
                    f"Found columns: {reader.fieldnames}"
                )
            rows = list(reader)
            original_fieldnames = list(reader.fieldnames)
    except FileNotFoundError:
        sys.exit(f"ERROR: Input file not found: '{input_path}'")

    summary = {"total": len(rows), "urgent": 0, "needs_review": 0, "errors": 0}
    output_fieldnames = original_fieldnames + ["category", "priority", "reason", "flag"]
    output_rows = []

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            result = {
                "category": "Other",
                "priority":  "Low",
                "reason":    f"Row classification error: {exc}",
                "flag":      "NEEDS_REVIEW",
            }
            summary["errors"] += 1

        row.update(result)
        output_rows.append(row)

        if result["priority"] == "Urgent":
            summary["urgent"] += 1
        if result["flag"] == "NEEDS_REVIEW":
            summary["needs_review"] += 1

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return summary


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    summary = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
    print(f"  Total rows   : {summary['total']}")
    print(f"  Urgent       : {summary['urgent']}")
    print(f"  Needs review : {summary['needs_review']}")
    print(f"  Row errors   : {summary['errors']}")
