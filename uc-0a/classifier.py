"""
UC-0A — Complaint Classifier
Classifies citizen complaints into category, priority, reason, and flag
based on a fixed taxonomy and severity-keyword rules.
"""
import argparse
import csv
import sys

# ── Classification Schema (from agents.md enforcement rules) ──────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Keyword → Category mapping ────────────────────────────────────────────
# Each entry: list of (keywords, category) checked in order; first match wins.

CATEGORY_RULES = [
    (["pothole", "pot hole", "crater", "sinkhole"],                  "Pothole"),
    (["flood", "waterlog", "water log", "submerge", "inundat"],      "Flooding"),
    (["streetlight", "street light", "lamp post", "lamppost",
      "light pole", "bulb out", "no light", "dark street",
      "broken light"],                                                "Streetlight"),
    (["garbage", "waste", "trash", "rubbish", "litter", "dump",
      "refuse", "debris", "filth", "sanitation"],                    "Waste"),
    (["noise", "loud", "honk", "music", "speaker", "blast",
      "disturb", "sound pollution", "noise pollution"],              "Noise"),
    (["road damage", "road crack", "broken road", "road surface",
      "asphalt", "tarmac", "pavement damage", "crumble",
      "erode", "erosion"],                                           "Road Damage"),
    (["heritage", "monument", "historical", "ancient", "temple",
      "fort", "archaeological", "heritage site"],                    "Heritage Damage"),
    (["heat", "heatwave", "heat wave", "sunstroke", "overheat",
      "hot road", "burning road", "thermal"],                        "Heat Hazard"),
    (["drain", "sewer", "manhole", "clog", "blocked drain",
      "nala", "nallah", "gutter", "overflow pipe",
      "drainage", "sewage"],                                         "Drain Blockage"),
]


# ── Skill: classify_complaint ─────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint row.

    Input:  dict with at least a 'description' key (string).
    Output: dict with keys — complaint_id, category, priority, reason, flag.

    Enforcement rules (agents.md):
      1. category must be one of ALLOWED_CATEGORIES — no variations.
      2. priority = Urgent if any severity keyword is present, else Standard.
      3. reason must cite specific words from the description.
      4. flag = NEEDS_REVIEW when category is Other / ambiguous.
    """
    complaint_id = row.get("complaint_id", row.get("id", ""))
    description = (row.get("description") or "").strip()

    # Handle empty / missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or missing; insufficient information to classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Determine category ────────────────────────────────────────────
    category = "Other"
    matched_keyword = None
    for keywords, cat in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keyword = kw
                break
        if category != "Other":
            break

    # ── Determine priority ────────────────────────────────────────────
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if severity_hits:
        priority = "Urgent"
    else:
        priority = "Standard"

    # ── Build reason citing specific words ─────────────────────────────
    if category != "Other" and matched_keyword:
        reason = (
            f"Description contains '{matched_keyword}' indicating {category}."
        )
    else:
        reason = "No recognized category keywords found in description."

    if severity_hits:
        reason += f" Severity keyword(s) detected: {', '.join(severity_hits)}."

    # ── Flag ambiguous ────────────────────────────────────────────────
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Skill: batch_classify ─────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint to each row, write results CSV.

    Error handling (skills.md):
      - Skips rows that fail to parse; logs a warning to stderr.
      - Exits non-zero if the input file cannot be read.
    """
    OUTPUT_FIELDS = [
        "complaint_id", "description",
        "category", "priority", "reason", "flag",
    ]

    try:
        infile = open(input_path, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Cannot read input file: {exc}", file=sys.stderr)
        sys.exit(1)

    results = []
    skipped = 0

    with infile:
        reader = csv.DictReader(infile)
        for row_num, row in enumerate(reader, start=2):  # row 1 = header
            try:
                result = classify_complaint(row)
                result["description"] = row.get("description", "")
                results.append(result)
            except Exception as exc:
                skipped += 1
                print(
                    f"WARNING: Skipping row {row_num}: {exc}",
                    file=sys.stderr,
                )

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints.", file=sys.stderr)
    if skipped:
        print(f"Skipped {skipped} row(s) due to errors.", file=sys.stderr)


# ── CLI entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
