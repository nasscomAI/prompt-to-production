"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify using keyword-based
RICE enforcement rules defined in agents.md and skills.md.
"""
import argparse
import csv
import logging
import sys

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# ── Enforcement constants (from agents.md & README) ──────────────────────────

CATEGORIES = [
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

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (order matters — first match wins)
CATEGORY_RULES = [
    ("Pothole",         ["pothole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlogged", "submerged", "knee-deep"]),
    ("Streetlight",     ["streetlight", "street light", "lamp", "light out", "lights out",
                         "flickering", "sparking", "dark at night"]),
    ("Waste",           ["garbage", "waste", "litter", "dump", "dumped", "overflowing bin",
                         "dead animal", "smell"]),
    ("Noise",           ["noise", "music", "loud", "midnight", "sound"]),
    ("Road Damage",     ["road", "crack", "cracked", "sinking", "surface", "manhole",
                         "footpath", "tyre damage", "broken tile", "upturned"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat", "temperature", "sun", "hot"]),
    ("Drain Blockage",  ["drain", "blocked drain", "drain blocked", "sewer"]),
]


# ── Core skill: classify_complaint ────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Enforcement rules (from agents.md):
    1. Category must be exactly one of the CATEGORIES list.
    2. Priority is Urgent if any URGENT_KEYWORDS appear in description.
    3. Every output has a reason sentence citing words from the description.
    4. If category is ambiguous, output category=Other and flag=NEEDS_REVIEW.

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = row.get("description", "").strip()

    # ── Handle missing/empty description ──────────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided.",
            "flag":         "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Determine category ────────────────────────────────────────────────────
    category = None
    matched_keyword = None
    for cat, keywords in CATEGORY_RULES:
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

    # ── Determine priority ────────────────────────────────────────────────────
    triggered_urgent = next(
        (kw for kw in URGENT_KEYWORDS if kw in desc_lower), None
    )
    if triggered_urgent:
        priority = "Urgent"
    else:
        # Heuristic: multi-person/infra impact → Standard; personal nuisance → Low
        standard_signals = [
            "commuters", "passengers", "residents", "shoppers", "vehicles",
            "public", "multiple", "stranded", "affecting", "three", "several",
        ]
        if any(sig in desc_lower for sig in standard_signals):
            priority = "Standard"
        else:
            priority = "Low"

    # ── Build reason sentence ─────────────────────────────────────────────────
    if flag == "NEEDS_REVIEW":
        reason = f"Description '{description[:80]}' does not match any known category; manual review required."
    elif triggered_urgent:
        reason = (
            f"Classified as {category} and marked Urgent because the description "
            f"contains the keyword '{triggered_urgent}': \"{description[:100]}\"."
        )
    else:
        reason = (
            f"Classified as {category} based on keyword '{matched_keyword}' "
            f"found in description: \"{description[:100]}\"."
        )

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── Core skill: batch_classify ────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Enforcement:
    - Flags null/empty descriptions as NEEDS_REVIEW.
    - Does not crash on bad rows — logs a warning and writes error placeholder.
    - Always produces an output file even if all rows fail.
    """
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to read input CSV: {e}")
        sys.exit(1)

    for row in rows:
        try:
            classification = classify_complaint(row)
            merged = {**row, **classification}
            # Remove duplicate complaint_id key if present
            results.append(merged)
        except Exception as e:
            logging.warning(
                f"Failed to classify row {row.get('complaint_id', '?')}: {e}"
            )
            results.append({
                **row,
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Processing error: {e}",
                "flag":         "NEEDS_REVIEW",
            })

    if not results:
        logging.warning("No rows were processed. Output file will be empty.")

    # ── Write output CSV ──────────────────────────────────────────────────────
    output_fields_order = [
        "complaint_id", "date_raised", "city", "ward", "location",
        "description", "reported_by", "days_open",
        "category", "priority", "reason", "flag",
    ]
    # Include any extra columns not in the predefined order
    if results:
        all_keys = list(results[0].keys())
        extra = [k for k in all_keys if k not in output_fields_order]
        fieldnames = output_fields_order + extra
    else:
        fieldnames = output_fields_order

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        logging.error(f"Failed to write output CSV: {e}")
        sys.exit(1)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
