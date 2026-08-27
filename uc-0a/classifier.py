"""
UC-0A — Complaint Classifier
Implements the RICE-governed classify_complaint and batch_classify skills.

Role   : Municipal complaint classification engine.
Intent : Produce category + priority + reason + flag for every complaint row.
Context: Uses only the complaint description. No external knowledge.
Enforce: Exact category strings · Severity keywords trigger Urgent · Reason cites description · Ambiguity → NEEDS_REVIEW
"""
import argparse
import csv
import re
import sys

# ── Schema constants (Enforcement Rule 1) ─────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST trigger Urgent (Enforcement Rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (ordered: more specific first)
CATEGORY_RULES = [
    (["heritage", "monument", "historical", "old city"],                    "Heritage Damage"),
    (["heat", "temperature", "heatwave", "heat island"],                    "Heat Hazard"),
    (["drain", "drainage", "manhole", "sewer", "blocked drain"],            "Drain Blockage"),
    (["pothole", "tyre", "crater"],                                         "Pothole"),
    (["flood", "flooded", "flooding", "waterlog", "knee-deep", "stranded"], "Flooding"),
    (["streetlight", "street light", "lamp", "light out", "sparking",
      "flickering", "dark", "lights out"],                                  "Streetlight"),
    (["garbage", "waste", "dump", "rubbish", "litter", "bin", "overflowing"],
                                                                            "Waste"),
    (["noise", "music", "loud", "midnight", "nighttime", "sound"],         "Noise"),
    (["road", "surface", "crack", "sinking", "broken", "upturned",
      "footpath", "tiles", "fell", "collapse"],                             "Road Damage"),
]


# ── Skill 1: classify_complaint ───────────────────────────────────────────────
def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    RICE enforcement rules applied:
      - category must be exactly one of the ALLOWED_CATEGORIES
      - priority is Urgent if any SEVERITY_KEYWORD appears in description
      - reason is one sentence citing specific words from description
      - flag is NEEDS_REVIEW when category is genuinely ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = (row.get("description") or "").strip()

    # Context rule: empty / unparseable description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description too ambiguous to classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Enforcement Rule 2: severity check (must run before category) ─────────
    urgent_triggered = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    matched_severity_kws = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    # ── Enforcement Rule 1: category matching ─────────────────────────────────
    category = None
    matched_category_kws = []
    for keywords, cat in CATEGORY_RULES:
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            category = cat
            matched_category_kws = hits
            break

    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # ── Enforcement Rule 3: reason must cite description words ────────────────
    cited = matched_category_kws or matched_severity_kws
    if cited:
        quote = ", ".join(f'"{w}"' for w in cited[:3])
        reason = f'Classified as {category} based on {quote} in the complaint description.'
    else:
        reason = f'Classified as {category}; no strong matching keywords found — review recommended.'
        flag = "NEEDS_REVIEW"

    # ── Enforcement Rule 4: ambiguity override ────────────────────────────────
    # If urgent keyword present but category is ambiguous, still mark NEEDS_REVIEW
    if urgent_triggered and flag == "NEEDS_REVIEW":
        priority = "Urgent"
    elif urgent_triggered:
        priority = "Urgent"
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── Skill 2: batch_classify ───────────────────────────────────────────────────
def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    - Never halts on a bad row; writes NEEDS_REVIEW for failures.
    - Preserves all original columns and appends: category, priority, reason, flag.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or "description" not in reader.fieldnames:
                print(
                    f"ERROR: '{input_path}' is missing a 'description' column.",
                    file=sys.stderr,
                )
                sys.exit(1)
            rows = list(reader)
            original_fields = list(reader.fieldnames)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]
    all_fields = original_fields + [f for f in OUTPUT_FIELDS if f not in original_fields]

    results = []
    for idx, row in enumerate(rows):
        try:
            classification = classify_complaint(row)
        except Exception as exc:
            print(f"WARN: Row {idx} ({row.get('complaint_id','?')}) failed: {exc}", file=sys.stderr)
            classification = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category":     "Other",
                "priority":     "Low",
                "reason":       "Classification error — manual review required.",
                "flag":         "NEEDS_REVIEW",
            }
        # Merge original row with classification output
        merged = dict(row)
        for field in OUTPUT_FIELDS:
            merged[field] = classification.get(field, "")
        results.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows -> {output_path}")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
