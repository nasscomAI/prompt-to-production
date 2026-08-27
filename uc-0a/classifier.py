"""
UC-0A - Complaint Classifier
Rule-based implementation guided by agents.md and skills.md (RICE + CRAFT workflow).

Classification schema (from README):
  category  : Pothole | Flooding | Streetlight | Waste | Noise | Road Damage |
               Heritage Damage | Heat Hazard | Drain Blockage | Other
  priority  : Urgent (if severity keywords present) | Standard | Low
  reason    : one sentence citing specific words from description
  flag      : NEEDS_REVIEW or blank
"""

import argparse
import csv
import sys

# ---------------------------------------------------------------------------
# Schema constants - must match README exactly
# ---------------------------------------------------------------------------

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

# Severity keywords that ALWAYS trigger Urgent priority (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword rules - ordered most specific to least specific.
# Each entry: (category_name, [trigger_keywords], reason_template)
# First matching rule wins.
CATEGORY_RULES = [
    (
        "Heritage Damage",
        ["heritage"],
        "Description mentions '{kw}', indicating damage to or concern about a heritage site.",
    ),
    (
        "Heat Hazard",
        ["heat", "temperature", "heat wave", "heatstroke"],
        "Description mentions '{kw}', indicating a heat-related public hazard.",
    ),
    (
        "Drain Blockage",
        ["drain block", "drain blocked", "blocked drain", "drain choked", "choked drain"],
        "Description mentions '{kw}', indicating a blocked drainage issue.",
    ),
    (
        "Flooding",
        ["flood", "waterlog", "waterlogged", "submerged", "knee-deep", "knee deep",
         "stranded", "inundated", "standing water", "water-logging"],
        "Description mentions '{kw}', indicating a flooding or waterlogging problem.",
    ),
    (
        "Pothole",
        ["pothole", "pot hole", "pot-hole"],
        "Description mentions '{kw}', indicating a pothole on the road.",
    ),
    (
        "Streetlight",
        ["streetlight", "street light", "street-light", "lamp post", "lamppost",
         "light out", "lights out", "sparking", "flickering"],
        "Description mentions '{kw}', indicating a streetlight malfunction.",
    ),
    (
        "Noise",
        ["noise", "music", "loud", "midnight", "sound", "nuisance"],
        "Description mentions '{kw}', indicating a noise complaint.",
    ),
    (
        "Waste",
        ["garbage", "waste", "dump", "overflowing bin", "overflowing garbage",
         "dead animal", "litter", "rubbish", "trash", "sanitation"],
        "Description mentions '{kw}', indicating a solid waste or sanitation problem.",
    ),
    (
        "Road Damage",
        ["road surface", "cracked", "sinking", "manhole", "footpath",
         "tiles broken", "upturned", "road damage",
         "pavement", "tarmac", "asphalt", "utility work"],
        "Description mentions '{kw}', indicating road surface damage or infrastructure failure.",
    ),
]

OUTPUT_FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _find_keyword(description, keywords):
    """Return the first keyword found (case-insensitive) in description, or None."""
    desc_lower = description.lower()
    for kw in keywords:
        if kw.lower() in desc_lower:
            return kw
    return None


def _get_id(row):
    """Safely extract complaint_id, handling UTF-8 BOM in CSV headers."""
    for key in row:
        if key.strip('\ufeff').strip() == "complaint_id":
            return row[key]
    return "UNKNOWN"


def _determine_category(description):
    """
    Apply category rules in order; return (category, reason, flag).
    Falls back to Other + NEEDS_REVIEW if nothing matches.
    """
    for category, keywords, reason_template in CATEGORY_RULES:
        matched = _find_keyword(description, keywords)
        if matched:
            reason = reason_template.replace("{kw}", matched)
            return category, reason, ""

    return (
        "Other",
        "Description does not clearly match any known complaint category.",
        "NEEDS_REVIEW",
    )


def _determine_priority(description):
    """Return Urgent if any severity keyword is present, else Standard."""
    if _find_keyword(description, SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row):
    """
    Classify a single complaint row.

    Input : dict with at minimum keys complaint_id and description.
    Output: dict with keys complaint_id, category, priority, reason, flag.

    Enforcement rules applied (from agents.md):
      1. Category is exactly one of 10 allowed strings - keyword-rule matched.
      2. Priority is Urgent when description contains severity keywords; else Standard.
      3. Reason cites specific words from the description.
      4. Flag is NEEDS_REVIEW when category is genuinely ambiguous (Other).
    """
    complaint_id = _get_id(row)
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided - cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, reason, flag = _determine_category(description)
    priority = _determine_priority(description)

    if priority == "Urgent":
        sev_kw = _find_keyword(description, SEVERITY_KEYWORDS)
        reason = reason + " Priority set to Urgent because description contains '" + sev_kw + "'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path, output_path):
    """
    Read input CSV, classify each row, write results CSV.

    Error handling: bad rows get Other/Low/NEEDS_REVIEW, never crashes.
    """
    results = []
    error_rows = []
    total = 0

    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print("ERROR: Input file not found: " + input_path, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("ERROR: Could not read input file: " + str(e), file=sys.stderr)
        sys.exit(1)

    for row in rows:
        total += 1
        try:
            result = classify_complaint(row)
        except Exception as exc:
            complaint_id = _get_id(row)
            result = {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": "Classification error: " + str(exc),
                "flag": "NEEDS_REVIEW",
            }
            error_rows.append(complaint_id)
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    print("Processed : " + str(total) + " rows")
    print("Errors    : " + str(len(error_rows)) + (" - " + str(error_rows) if error_rows else ""))
    print("Urgent    : " + str(sum(1 for r in results if r["priority"] == "Urgent")))
    print("NeedsReview: " + str(sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to " + args.output)
