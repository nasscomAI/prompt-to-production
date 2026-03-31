"""
UC-0A — Complaint Classifier
Classifies citizen complaints into predefined categories with priority levels.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys


# ── Category keyword mappings ──────────────────────────────────────────────
# Order matters: more specific categories checked first to avoid false matches.
CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole", "potholes",
    ],
    "Flooding": [
        "flood", "flooded", "flooding", "waterlogged", "waterlogging",
        "submerged", "stranded", "knee-deep", "rainwater",
    ],
    "Drain Blockage": [
        "drain blocked", "drain blockage", "blocked drain", "drain completely blocked",
        "stormwater drain", "main drain blocked", "drain 100% blocked",
    ],
    "Streetlight": [
        "streetlight", "streetlights", "street light", "street lights",
        "unlit", "lights out", "darkness", "wiring theft", "substation",
        "sparking", "flickering",
    ],
    "Road Damage": [
        "road surface", "road subsidence", "road subsid", "road collapsed",
        "tarmac", "surface cracked", "surface buckled", "surface bubbling",
        "sinking", "subsid", "crater", "broken footpath", "footpath broken",
        "paving", "manhole cover missing", "missing manhole",
        "cobblestones broken", "tiles broken", "upturned", "road dividers",
        "glass broken", "roof broken", "shelter", "split branches",
        "fall risk", "dead tree",
    ],
    "Waste": [
        "waste", "garbage", "overflowing", "bins overflowing", "rubbish",
        "trash", "not cleared", "dead animal", "smell", "health risk",
        "litter",
    ],
    "Noise": [
        "noise", "music", "loud", "drilling", "amplifier", "amplifiers",
        "band playing", "audible", "decibel", "idling",
    ],
    "Heritage Damage": [
        "heritage", "museum", "historic", "ancient", "monument",
        "lamp post knocked", "defaced", "billboard", "heritage stone",
        "heritage zone",
    ],
    "Heat Hazard": [
        "heat", "melting", "temperature", "44°c", "45°c", "52°c",
        "overheated", "burns on contact", "sticking", "storing heat",
        "dangerous temperatures",
    ],
}

# Severity keywords that must trigger Urgent priority (from README spec)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
    "hospitalised", "collapsed",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")
    desc_lower = description.lower()

    # ── 1. Determine category ──────────────────────────────────────────
    category = "Other"
    matched_keywords = []

    # Check Drain Blockage before Flooding (drain blockage is more specific)
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in desc_lower:
                if category == "Other" or cat == category:
                    category = cat
                    matched_keywords.append(kw)

        if category != "Other" and cat == category:
            break  # first matched category wins

    # ── 2. Determine priority ──────────────────────────────────────────
    priority = "Standard"
    severity_matches = []

    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            severity_matches.append(kw)

    # Downgrade to Low if no urgency and complaint seems minor
    if priority == "Standard":
        days_open = 0
        try:
            days_open = int(row.get("days_open", 0))
        except (ValueError, TypeError):
            pass
        low_indicators = ["cosmetic", "minor", "paint", "faded"]
        if any(ind in desc_lower for ind in low_indicators) and days_open < 7:
            priority = "Low"

    # ── 3. Build reason ────────────────────────────────────────────────
    unique_keywords = list(dict.fromkeys(matched_keywords))
    cited: list[str] = [unique_keywords[i] for i in range(min(2, len(unique_keywords)))]
    if severity_matches:
        unique_severity = list(dict.fromkeys(severity_matches))
        cited.append(unique_severity[0])

    if cited:
        reason = (
            f"Classified as '{category}' ({priority}) because description "
            f"mentions: {', '.join(repr(w) for w in cited)}."
        )
    else:
        reason = (
            f"Classified as '{category}' ({priority}) — no strong keyword "
            f"match found in description."
        )

    # ── 4. Set flag ────────────────────────────────────────────────────
    flag = "NEEDS_REVIEW" if category == "Other" else ""

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
    errors = []

    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for i, row in enumerate(reader, start=2):  # line 2 = first data row
                try:
                    if not row.get("description"):
                        result = {
                            "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Empty description — cannot classify.",
                            "flag": "NEEDS_REVIEW",
                        }
                    else:
                        result = classify_complaint(row)
                    results.append(result)
                except Exception as exc:
                    print(
                        f"WARNING: Skipping row {i}: {exc}",
                        file=sys.stderr,
                    )
                    errors.append(i)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints. Errors: {len(errors)}.")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
