"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

# ── Enforcement constants (from agents.md) ──────────────────────────────────

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# ── Category keyword map ─────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "pot hole", "potholes", "crater"],
    "Flooding":        ["flood", "flooding", "waterlogged", "water logging", "inundated", "submerged", "waterlog"],
    "Streetlight":     ["streetlight", "street light", "lamp post", "lamp", "light not working", "dark street", "lighting", "no light"],
    "Waste":           ["waste", "garbage", "trash", "litter", "dump", "rubbish", "refuse", "sewage smell"],
    "Noise":           ["noise", "loud", "sound", "disturbance", "blaring", "horn", "music"],
    "Road Damage":     ["road damage", "cracked road", "broken road", "damaged road", "road broken", "road cracked", "road collapsed", "road surface"],
    "Heritage Damage": ["heritage", "monument", "historic", "heritage site", "ancient", "protected structure"],
    "Heat Hazard":     ["heat", "temperature", "hot", "burning", "scorching", "heatwave"],
    "Drain Blockage":  ["drain", "drainage", "blocked drain", "sewer", "manhole", "overflow drain", "clogged drain", "drain blocked"],
}


# ── Skill 1: classify_complaint ──────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Enforcement rules applied:
    - Category must be exactly one of VALID_CATEGORIES (no variations)
    - Priority is Urgent if any URGENT_KEYWORDS found in description
    - Priority is Standard by default
    - Reason is one sentence citing specific words from the description
    - Flag is NEEDS_REVIEW if category is genuinely ambiguous
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description  = str(row.get("description", "")).strip()
    desc_lower   = description.lower()

    # ── Guard: missing or empty description ────────────────────────────────
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Standard",
            "reason":       "No description provided; defaulting to Other for review.",
            "flag":         "NEEDS_REVIEW",
        }

    # ── Category detection ─────────────────────────────────────────────────
    matched_categories = []
    matched_keywords   = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            matched_categories.append(category)
            matched_keywords[category] = hits

    flag = ""

    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Multiple categories matched — ambiguous, pick first but flag
        category = matched_categories[0]
        flag     = "NEEDS_REVIEW"
    else:
        # No keyword matched — Other, flag for review
        category = "Other"
        flag     = "NEEDS_REVIEW"

    # ── Priority detection ─────────────────────────────────────────────────
    urgent_hits = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    priority    = "Urgent" if urgent_hits else "Standard"

    # ── Reason: one sentence citing specific words from description ─────────
    cited_keyword = ""
    if category in matched_keywords and matched_keywords[category]:
        cited_keyword = matched_keywords[category][0]
    elif urgent_hits:
        cited_keyword = urgent_hits[0]
    else:
        words = [w for w in description.split() if len(w) > 4]
        cited_keyword = words[0] if words else description[:20]

    if flag == "NEEDS_REVIEW" and category == "Other":
        reason = (
            f"Description mentions '{cited_keyword if cited_keyword else description[:30]}' "
            f"which does not clearly match any standard category; flagged for review."
        )
    elif flag == "NEEDS_REVIEW":
        reason = (
            f"Description contains '{cited_keyword}' which could match multiple categories; "
            f"classified as {category} but flagged for human review."
        )
    elif priority == "Urgent":
        reason = (
            f"Description mentions '{urgent_hits[0]}' indicating a safety-critical situation, "
            f"classified as {category} with Urgent priority."
        )
    else:
        reason = (
            f"Description mentions '{cited_keyword}', "
            f"which matches the {category} category."
        )

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── Skill 2: batch_classify ──────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Error handling:
    - Aborts with clear message if input file cannot be read
    - Skips rows missing the description column and logs them
    - Ensures every output row has a reason (no silent blanks)
    - Does not crash on bad rows — logs and continues
    """

    # ── Read input ──────────────────────────────────────────────────────────
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader  = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                print(f"ERROR: Input file '{input_path}' is empty or has no headers.")
                sys.exit(1)

            desc_col = None
            for col in headers:
                if col.strip().lower() == "description":
                    desc_col = col
                    break

            if not desc_col:
                print(f"ERROR: Input CSV must contain a 'description' column. Found: {headers}")
                sys.exit(1)

            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: '{input_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}")
        sys.exit(1)

    if not rows:
        print("ERROR: Input CSV has no data rows.")
        sys.exit(1)

    # ── Classify each row ───────────────────────────────────────────────────
    output_rows = []
    errors      = 0

    for i, row in enumerate(rows, start=1):
        try:
            normalised = {k.strip().lower(): v for k, v in row.items()}
            clean_row  = {
                "complaint_id": normalised.get("complaint_id", f"ROW_{i}"),
                "description":  normalised.get("description", ""),
            }
            result = classify_complaint(clean_row)

            # Enforcement: reason must never be blank
            if not result.get("reason"):
                result["reason"] = "Classification completed; no specific reason generated."
                result["flag"]   = "NEEDS_REVIEW"

            output_rows.append(result)

        except Exception as e:
            print(f"  WARNING: Row {i} failed — {e}. Marking NEEDS_REVIEW.")
            errors += 1
            output_rows.append({
                "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                "category":     "Other",
                "priority":     "Standard",
                "reason":       f"Row could not be processed due to an error: {e}",
                "flag":         "NEEDS_REVIEW",
            })

    # ── Write output ────────────────────────────────────────────────────────
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}")
        sys.exit(1)

    print(f"  Processed : {len(output_rows)} rows")
    print(f"  Errors    : {errors} rows (written as NEEDS_REVIEW)")
    print(f"  Output    : {output_path}")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    print(f"Running UC-0A Complaint Classifier")
    print(f"  Input  : {args.input}")
    print(f"  Output : {args.output}")

    batch_classify(args.input, args.output)
    print("Done.")