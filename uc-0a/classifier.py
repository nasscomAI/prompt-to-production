"""
UC-0A -- Complaint Classifier
Built from agents.md (RICE enforcement) and skills.md (skill definitions).

Agent Role:
  Municipal complaint classification agent. Operates strictly within the
  defined taxonomy and severity rules. Uses only the complaint description
  text -- no external knowledge or assumptions.

Enforcement Rules:
  1. Category must be exactly one of the 10 allowed values.
  2. Priority = Urgent if severity keywords are present.
  3. Every row must have a reason citing specific words from the description.
  4. Ambiguous complaints get flag = NEEDS_REVIEW.
  5. Fallback category is Other.
"""

import argparse
import csv
import re
import sys


# ---------------------------------------------------------------------------
#  Constants — derived from README Classification Schema
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ---------------------------------------------------------------------------
#  Category keyword map — maps description keywords to categories
#  Order matters: more specific patterns are checked first.
# ---------------------------------------------------------------------------

CATEGORY_RULES = [
    {
        "category": "Heritage Damage",
        "keywords": ["heritage", "monument", "historical", "ancient", "archaeological"],
    },
    {
        "category": "Heat Hazard",
        "keywords": ["heat", "heatwave", "sunstroke", "heat stroke", "overheating",
                      "temperature", "scorching"],
    },
    {
        "category": "Drain Blockage",
        "keywords": ["drain blocked", "drain blockage", "blocked drain", "clogged drain",
                      "drain overflow", "manhole", "sewer", "sewage", "nala"],
    },
    {
        "category": "Flooding",
        "keywords": ["flood", "flooded", "flooding", "waterlogged", "waterlogging",
                      "water logging", "submerged", "inundated", "knee-deep",
                      "waist-deep", "stranded"],
    },
    {
        "category": "Pothole",
        "keywords": ["pothole", "pot hole", "pot-hole"],
    },
    {
        "category": "Streetlight",
        "keywords": ["streetlight", "street light", "street-light", "lamp post",
                      "light out", "lights out", "flickering", "sparking",
                      "no light", "dark at night", "no lighting"],
    },
    {
        "category": "Noise",
        "keywords": ["noise", "loud music", "loudspeaker", "honking", "midnight",
                      "music past", "noise pollution", "blaring"],
    },
    {
        "category": "Road Damage",
        "keywords": ["road damage", "road surface", "cracked road", "sinking road",
                      "broken road", "road crack", "road caved", "road sinking",
                      "footpath", "tiles broken", "upturned", "pavement damage",
                      "road broken"],
    },
    {
        "category": "Waste",
        "keywords": ["garbage", "waste", "trash", "rubbish", "dumped", "littering",
                      "overflowing", "dead animal", "debris", "refuse", "bulk waste",
                      "not removed", "smell"],
    },
]


# ---------------------------------------------------------------------------
#  Skill: classify_complaint
#  Input:  A single row (dict) with at least a 'description' field.
#  Output: dict with keys: complaint_id, category, priority, reason, flag
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md):
      - Category must be exactly one of the 10 allowed values
      - Priority = Urgent if severity keywords found (case-insensitive)
      - Reason must cite specific words from the description
      - Flag = NEEDS_REVIEW for ambiguous or empty descriptions
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # --- Handle empty / missing description ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or unintelligible.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Step 1: Determine category ---
    matched_categories = []
    matched_keywords_map = {}

    for rule in CATEGORY_RULES:
        found_keywords = [kw for kw in rule["keywords"] if kw in desc_lower]
        if found_keywords:
            matched_categories.append(rule["category"])
            matched_keywords_map[rule["category"]] = found_keywords

    if len(matched_categories) == 0:
        category = "Other"
        category_keywords = []
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        category_keywords = matched_keywords_map[category]
        flag = ""
    else:
        # Multiple categories matched — pick the first (highest priority) but flag
        category = matched_categories[0]
        category_keywords = matched_keywords_map[category]
        flag = "NEEDS_REVIEW"

    # --- Step 2: Determine priority via severity keywords ---
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_severity:
        priority = "Urgent"
    else:
        # Heuristic: if days_open > 14 or certain urgency words, Standard; else Low
        days_open = 0
        try:
            days_open = int(row.get("days_open", 0))
        except (ValueError, TypeError):
            pass

        if days_open > 14 or any(w in desc_lower for w in [
            "risk", "danger", "damage", "accident", "blocked", "stranded",
            "affecting", "concern", "safety"
        ]):
            priority = "Standard"
        else:
            priority = "Low"

    # --- Step 3: Build reason citing specific words ---
    reason_parts = []

    if category_keywords:
        reason_parts.append(
            f"Description mentions '{category_keywords[0]}' indicating {category}"
        )

    if found_severity:
        severity_str = "', '".join(found_severity)
        reason_parts.append(
            f"severity keyword(s) '{severity_str}' trigger Urgent priority"
        )
    elif priority == "Standard":
        reason_parts.append("context suggests moderate impact warranting Standard priority")

    if not reason_parts:
        reason_parts.append(
            "Description does not clearly match any specific category"
        )

    reason = "; ".join(reason_parts) + "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
#  Skill: batch_classify
#  Input:  input_path (str), output_path (str)
#  Output: CSV file written at output_path
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint to each row, write results CSV.

    Error handling (from skills.md):
      - If input file missing or invalid, raise clear error and exit.
      - If a row fails, set defaults and continue processing remaining rows.
    """
    # --- Validate input file ---
    try:
        infile = open(input_path, "r", encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot open input file: {e}")
        sys.exit(1)

    try:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            print(f"ERROR: Input file is empty or not a valid CSV: {input_path}")
            sys.exit(1)
    except csv.Error as e:
        print(f"ERROR: Invalid CSV format: {e}")
        sys.exit(1)

    # --- Process rows ---
    results = []
    row_count = 0
    error_count = 0

    for row in reader:
        row_count += 1
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            error_count += 1
            complaint_id = row.get("complaint_id", f"ROW_{row_count}")
            print(f"WARNING: Row {row_count} ({complaint_id}) failed: {e}")
            results.append({
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": "Classification failed -- missing or invalid description.",
                "flag": "NEEDS_REVIEW",
            })

    infile.close()

    # --- Write output CSV ---
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}")
        sys.exit(1)

    # --- Summary ---
    print(f"Processed {row_count} complaints.")
    if error_count:
        print(f"  {error_count} row(s) had errors and were flagged NEEDS_REVIEW.")
    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"  {urgent_count} classified as Urgent.")
    print(f"  {review_count} flagged for review.")


# ---------------------------------------------------------------------------
#  Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
