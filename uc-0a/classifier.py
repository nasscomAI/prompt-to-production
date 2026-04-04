"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category and priority using rule-based keyword matching.
Follows the RICE enforcement rules defined in agents.md.
"""
import argparse
import csv
import re
import sys

# --- Classification Schema ---

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword map: keyword -> category
# Order matters — more specific patterns first to avoid false matches
CATEGORY_RULES = [
    # Heritage Damage
    (["heritage"], "Heritage Damage"),
    # Heat Hazard
    (["heat", "heatwave", "sunstroke", "heat stroke", "temperature"], "Heat Hazard"),
    # Drain Blockage
    (["drain", "drainage", "blocked drain", "clogged drain", "nala", "nallah"], "Drain Blockage"),
    # Streetlight
    (["streetlight", "street light", "light out", "lights out", "lamp", "lighting",
      "flickering", "sparking", "dark at night", "very dark"], "Streetlight"),
    # Pothole
    (["pothole", "pot hole", "crater"], "Pothole"),
    # Flooding
    (["flood", "flooded", "waterlog", "water log", "submerged", "knee-deep",
      "waist-deep", "stranded", "inundated"], "Flooding"),
    # Waste
    (["garbage", "waste", "trash", "rubbish", "dump", "dumped", "litter",
      "overflowing", "dead animal", "smell", "stink", "stench"], "Waste"),
    # Noise
    (["noise", "loud", "music", "honking", "midnight", "decibel", "sound pollution"], "Noise"),
    # Road Damage
    (["road surface", "cracked", "sinking", "broken road", "road damage",
      "uneven road", "road caved", "footpath", "tiles broken", "upturned",
      "manhole", "missing cover"], "Road Damage"),
]


def _match_category(description: str):
    """Match description to a category. Returns (category, matched_keywords) or (None, [])."""
    desc_lower = description.lower()
    matches = []

    for keywords, category in CATEGORY_RULES:
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            matches.append((category, matched))

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # If multiple categories match, check if one is clearly dominant
        # Return the first match (most specific due to ordering), but flag if close
        return matches[0][0], matches[0][1], len(matches) > 1
    return None, [], False


def _check_severity(description: str):
    """Check if any severity keywords are present. Returns list of matched keywords."""
    desc_lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Determine category
    cat_result = _match_category(description)
    if len(cat_result) == 3:
        category, matched_kw, ambiguous = cat_result
    else:
        category, matched_kw = cat_result
        ambiguous = False

    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif ambiguous:
        flag = "NEEDS_REVIEW"

    # Determine priority
    severity_hits = _check_severity(description)
    if severity_hits:
        priority = "Urgent"
    else:
        # Use days_open and impact indicators for Standard vs Low
        days_open = 0
        try:
            days_open = int(row.get("days_open", 0))
        except (ValueError, TypeError):
            pass

        # Standard if there's community impact or long-standing issue
        impact_words = ["risk", "affected", "stranded", "commuters", "passengers",
                        "residents", "pedestrians", "safety", "concern", "inaccessible",
                        "health", "blocked"]
        desc_lower = description.lower()
        has_impact = any(w in desc_lower for w in impact_words)

        if has_impact or days_open >= 7:
            priority = "Standard"
        else:
            priority = "Low"

    # Build reason citing specific words from description
    reason_parts = []
    if matched_kw:
        reason_parts.append(f"Description mentions '{', '.join(matched_kw[:2])}'")
    if severity_hits:
        reason_parts.append(f"severity keyword '{', '.join(severity_hits)}' triggers Urgent")
    elif priority == "Standard":
        reason_parts.append("community impact indicated")

    if not reason_parts:
        reason_parts.append(f"Description: '{description[:60]}...'")

    reason = "; ".join(reason_parts) + f" — classified as {category}/{priority}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    errors = 0

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                errors += 1
                print(f"WARNING: Row {i} failed: {e}", file=sys.stderr)
                # Still produce a row with error info
                results.append({
                    "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification error: {e}",
                    "flag": "NEEDS_REVIEW"
                })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    if errors:
        print(f"Completed with {errors} error(s). Check stderr for details.", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
