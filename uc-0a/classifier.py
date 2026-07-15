"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify using RICE enforcement rules
defined in agents.md and skills.md.
"""
import argparse
import csv
import sys
import os

# ──────────────────────────────────────────────
# ENFORCEMENT CONSTANTS (from agents.md)
# ──────────────────────────────────────────────

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

# Keywords that MUST trigger Urgent priority (case-insensitive, partial match)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Mapping: keyword hints → category (first match wins; order matters)
CATEGORY_HINTS = [
    (["pothole", "pot hole", "tyre damage", "tyre"],              "Pothole"),
    (["flood", "flooded", "waterlog", "standing water", "knee-deep", "inundated"], "Flooding"),
    (["drain blockage", "drain blocked", "blocked drain", "blocked"],              "Drain Blockage"),
    (["streetlight", "street light", "lamp post", "lighting", "light out",
      "light flickering", "sparking", "lights out"],                               "Streetlight"),
    (["waste", "garbage", "rubbish", "litter", "dumped", "overflowing bin",
      "dead animal", "health concern"],                                             "Waste"),
    (["noise", "music", "loud", "midnight", "sound"],                              "Noise"),
    (["road damage", "road surface", "road cracked", "cracked", "sinking",
      "manhole", "footpath", "tiles broken", "upturned", "utility work"],          "Road Damage"),
    (["heritage", "old city", "heritage street"],                                  "Heritage Damage"),
    (["heat", "temperature", "sun", "shade"],                                      "Heat Hazard"),
]


def _check_urgent(description: str) -> bool:
    """Return True if any urgent keyword is found in the description."""
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in URGENT_KEYWORDS)


def _detect_category(description: str):
    """
    Return (category, is_ambiguous).
    Tries to find a unique matching category from CATEGORY_HINTS.
    If multiple top-level categories match, returns best guess + is_ambiguous=True.
    """
    desc_lower = description.lower()
    matched = []
    for keywords, category in CATEGORY_HINTS:
        if any(kw in desc_lower for kw in keywords):
            if category not in matched:
                matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    elif len(matched) > 1:
        return matched[0], True   # best guess is first match; flag ambiguity
    else:
        return "Other", True      # nothing matched → Other + NEEDS_REVIEW


def _extract_reason(description: str, category: str, priority: str, is_ambiguous: bool) -> str:
    """
    Build a one-sentence reason that cites specific words from the description.
    Enforcement: must cite at least one word/phrase directly from description.
    """
    # Find the most relevant quoted phrase (3-6 words from description)
    words = description.split()
    # Pick a meaningful excerpt: first 8 words as anchor quote
    excerpt = " ".join(words[:8]) if len(words) >= 8 else description

    if is_ambiguous:
        return (
            f'Classified as "{category}" based on "{excerpt}" — '
            f"description matches multiple categories; marked for review."
        )

    priority_note = ""
    if priority == "Urgent":
        triggered = [kw for kw in URGENT_KEYWORDS if kw in description.lower()]
        priority_note = f"; severity keyword '{triggered[0]}' triggers Urgent priority"

    return f'Classified as "{category}" based on "{excerpt}"{priority_note}.'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input  : dict with keys complaint_id (str) and description (str)
    Output : dict with keys complaint_id, category, priority, reason, flag

    Enforcement rules from agents.md:
    1. Category must be exactly one of the ten allowed values.
    2. Priority = Urgent if any urgent keyword present in description.
    3. Reason must cite specific words from description.
    4. flag = NEEDS_REVIEW when category is ambiguous or description missing.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # ── Rule: Missing description ──────────────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "No description provided.",
            "flag":         "NEEDS_REVIEW",
        }

    # ── Rule 1: Detect category ────────────────────────────────────────────
    category, is_ambiguous = _detect_category(description)

    # ── Rule 2: Determine priority ─────────────────────────────────────────
    if _check_urgent(description):
        priority = "Urgent"
    else:
        priority = "Standard"

    # ── Rule 3: Build reason ───────────────────────────────────────────────
    reason = _extract_reason(description, category, priority, is_ambiguous)

    # ── Rule 4: Set flag ───────────────────────────────────────────────────
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Must:
    - Flag nulls / missing fields
    - Not crash on bad rows
    - Produce output even if some rows fail
    - Print summary to stdout
    """
    # ── Validate input file ────────────────────────────────────────────────
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # ── Validate output directory ──────────────────────────────────────────
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as exc:
            print(f"ERROR: Cannot create output directory '{output_dir}': {exc}", file=sys.stderr)
            sys.exit(1)

    results       = []
    skipped_rows  = []
    total_rows    = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for idx, raw_row in enumerate(reader, start=2):   # row 1 = header
            total_rows += 1
            # Normalise: strip whitespace from all values
            row = {k: (v.strip() if v else "") for k, v in raw_row.items()}

            # Remap columns: CSV uses 'complaint_id' and 'description'
            complaint_id = row.get("complaint_id", "").strip()
            description  = row.get("description", "").strip()

            if not complaint_id:
                print(f"  WARNING row {idx}: missing complaint_id — row skipped, no output written.")
                skipped_rows.append(idx)
                continue

            result = classify_complaint({
                "complaint_id": complaint_id,
                "description":  description,
            })
            results.append(result)

    # ── Write output CSV ───────────────────────────────────────────────────
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    # ── Print summary ──────────────────────────────────────────────────────
    urgent_count      = sum(1 for r in results if r["priority"] == "Urgent")
    needs_review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")

    print(f"\n{'-'*55}")
    print(f"  UC-0A Complaint Classifier -- Run Summary")
    print(f"{'-'*55}")
    print(f"  Input file   : {input_path}")
    print(f"  Output file  : {output_path}")
    print(f"  Total rows   : {total_rows}")
    print(f"  Classified   : {len(results)}")
    print(f"  Urgent       : {urgent_count}")
    print(f"  NEEDS_REVIEW : {needs_review_count}")
    if skipped_rows:
        print(f"  Skipped rows : {len(skipped_rows)} (rows {skipped_rows})")
    print(f"{'-'*55}\n")

    # ── Print classified results table ─────────────────────────────────────
    print(f"{'ID':<12} {'CATEGORY':<18} {'PRIORITY':<10} {'FLAG'}")
    print(f"{'-'*12} {'-'*18} {'-'*10} {'-'*12}")
    for r in results:
        print(f"{r['complaint_id']:<12} {r['category']:<18} {r['priority']:<10} {r['flag']}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
