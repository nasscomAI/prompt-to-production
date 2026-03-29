"""
UC-0A — Complaint Classifier
Classifies civic complaints by category, priority, reason, and review flag.
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# ── Allowed taxonomy (exact strings only) ──────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# ── Severity keywords that force Urgent priority ───────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Keyword → category mapping (order matters: first match wins) ──
# Each entry: (list_of_keywords, category)
CATEGORY_RULES = [
    # Drain Blockage must come BEFORE Flooding so "drain blocked" is not
    # mis-classified as Flooding when there's no actual flooding described.
    (["drain blocked", "drain blockage", "blocked drain", "drain block",
      "stormwater drain", "drain clogged", "main drain blocked"], "Drain Blockage"),

    # Flooding
    (["flood", "flooded", "flooding", "waterlogged", "waterlogging",
      "submerged", "inundated", "water stagnation", "rainwater",
      "flooding risk"], "Flooding"),

    # Road Damage (must come BEFORE Pothole to catch "road collapse")
    (["road collapse", "road collapsed", "road damage", "road cave",
      "crater", "road sunk", "road subsidence"], "Road Damage"),

    # Pothole
    (["pothole", "potholes"], "Pothole"),

    # Heritage Damage
    (["heritage", "monument", "archaeological", "historical structure"],
     "Heritage Damage"),

    # Waste
    (["waste", "garbage", "rubbish", "trash", "litter", "dumping",
      "debris", "refuse"], "Waste"),

    # Streetlight
    (["streetlight", "street light", "lamp post", "lighting",
      "dark road", "no light"], "Streetlight"),

    # Noise
    (["noise", "loud", "drilling", "honking", "disturbance",
      "sound pollution", "idling", "engines on"], "Noise"),

    # Heat Hazard
    (["heat", "heatwave", "sunstroke", "heat hazard",
      "hot surface", "temperature"], "Heat Hazard"),
]


def _match_category(description: str):
    """Return (category, matched_keywords, ambiguous) from description."""
    desc_lower = description.lower()
    matches = []

    for keywords, category in CATEGORY_RULES:
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            matches.append((category, matched))

    if not matches:
        return "Other", [], True
    if len(matches) == 1:
        return matches[0][0], matches[0][1], False

    # Multiple categories matched — pick best fit (most keyword hits)
    # but flag as ambiguous if tied
    matches.sort(key=lambda x: len(x[1]), reverse=True)
    best = matches[0]
    second = matches[1]
    ambiguous = len(best[1]) == len(second[1])
    return best[0], best[1], ambiguous


def _check_severity(description: str) -> list:
    """Return list of severity keywords found in description."""
    desc_lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty/missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine category
    category, matched_kws, ambiguous = _match_category(description)

    # Determine priority via severity keywords
    severity_hits = _check_severity(description)
    if severity_hits:
        priority = "Urgent"
    elif category == "Other":
        priority = "Standard"
    else:
        # Default to Standard; Low only for clearly minor items
        priority = "Standard"

    # Build reason citing specific words from description
    if matched_kws:
        reason = (
            f"Classified as {category} because description mentions: "
            f"{', '.join(matched_kws)}."
        )
    else:
        reason = (
            f"Classified as Other because no category keywords matched "
            f"in the description."
        )

    if severity_hits:
        reason += (
            f" Marked Urgent due to severity keyword(s): "
            f"{', '.join(severity_hits)}."
        )

    # Set flag
    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some fail.
    """
    results = []
    failed = 0
    processed = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            processed += 1
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                failed += 1
                cid = row.get("complaint_id", f"ROW-{processed}")
                print(f"  WARN: Failed to classify {cid}: {e}")
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    succeeded = processed - failed
    print(f"  Processed: {processed} | Succeeded: {succeeded} | Failed: {failed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
