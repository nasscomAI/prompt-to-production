"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category and priority using the RICE enforcement
rules defined in agents.md and skills.md.
"""
import argparse
import csv
import logging
import re
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Allowed taxonomy (exact strings only) ──────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# ── Severity keywords that force Urgent priority ───────────────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

# ── Category detection rules (order matters — first match wins) ────────────
# Each entry: (category, list-of-indicator-phrases)
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Heritage Damage", [
        "heritage", "historic", "heritage zone", "heritage stone",
        "heritage lamp", "heritage residential", "heritage precinct",
        "cobblestone", "tram road", "tagore", "marble palace",
        "defaced", "billboard", "lamp post knocked",
        "step well", "ancient",
    ]),
    ("Pothole", [
        "pothole", "potholes",
    ]),
    ("Heat Hazard", [
        "heat", "sunstroke", "heatstroke", "temperature",
        "shade", "scorching", "melting", "°c", "burns",
        "full sun", "exposed to full sun", "bubbling",
        "storing heat", "unbearable",
    ]),
    ("Flooding", [
        "flood", "flooded", "waterlogged", "submerge", "inundate",
        "water level", "waterlog", "knee-deep", "waist-deep",
        "rainwater",
    ]),
    ("Drain Blockage", [
        "drain", "drainage", "blocked drain", "clogged drain",
        "draining directly", "nala", "sewer", "sewage",
        "stormwater drain", "mosquito breeding",
    ]),
    ("Streetlight", [
        "streetlight", "street light", "lamp", "lighting",
        "darkness", "substation tripped", "no light", "bulb",
        "unlit", "lights out", "wiring theft",
    ]),
    ("Waste", [
        "waste", "garbage", "trash", "rubbish", "litter",
        "overflowing", "dump", "debris", "not cleared",
        "dead animal", "not removed", "overflow", "health risk",
        "bins overflowing",
    ]),
    ("Noise", [
        "noise", "loud", "amplifier", "speaker", "band playing",
        "decibel", "honking", "blaring", "music",
        "drilling",
    ]),
    ("Road Damage", [
        "road surface", "road damage", "road subsid", "buckled",
        "broken road", "cave-in", "sinking", "crumbled",
        "footpath broken", "paving removed", "road collapsed",
        "crater", "manhole", "tiles broken", "upturned",
        "subsidence", "broken bench", "split branches",
        "fall risk",
    ]),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Determine the complaint category from the description text.
    Returns (category, is_ambiguous).
    """
    desc_lower = description.lower()

    matched_categories: list[str] = []
    for category, indicators in CATEGORY_RULES:
        for phrase in indicators:
            if phrase in desc_lower:
                if category not in matched_categories:
                    matched_categories.append(category)
                break  # move to next category rule

    if len(matched_categories) == 1:
        return matched_categories[0], False
    elif len(matched_categories) > 1:
        # Multiple categories matched — use the first (highest-priority) match
        # but still not ambiguous since our rule ordering resolves it
        return matched_categories[0], False
    else:
        return "Other", True


def _detect_priority(description: str) -> str:
    """
    Determine priority. Urgent if any severity keyword is present;
    otherwise Standard.
    """
    desc_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        # Use word-boundary matching so "fire" doesn't match "firewall" etc.
        if re.search(rf"\b{re.escape(keyword)}\b", desc_lower):
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a single-sentence reason citing specific words from the description.
    """
    desc_lower = description.lower()

    # Find which category indicator matched
    cat_evidence = None
    for cat, indicators in CATEGORY_RULES:
        if cat == category:
            for phrase in indicators:
                if phrase in desc_lower:
                    cat_evidence = phrase
                    break
            break

    # Find which severity keyword matched (if Urgent)
    sev_evidence = None
    if priority == "Urgent":
        for keyword in SEVERITY_KEYWORDS:
            if re.search(rf"\b{re.escape(keyword)}\b", desc_lower):
                sev_evidence = keyword
                break

    # Compose reason
    if category == "Other" and cat_evidence is None:
        reason = "Description does not match any predefined category indicators."
    elif sev_evidence:
        reason = (
            f"Classified as {category} due to mention of \"{cat_evidence}\" "
            f"and marked Urgent because description contains \"{sev_evidence}\"."
        )
    else:
        reason = (
            f"Classified as {category} due to mention of \"{cat_evidence}\" in the description."
        )

    return reason


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md):
    - Category must be from the allowed list
    - Priority is Urgent if severity keywords are present
    - Reason must cite specific words from the description
    - Flag is NEEDS_REVIEW when category is genuinely ambiguous / Other
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # Handle missing / empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if (is_ambiguous or category == "Other") else ""

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
    - Flags nulls (empty descriptions) gracefully
    - Does not crash on bad rows — logs and skips
    - Produces output even if some rows fail
    """
    # Verify input file exists
    try:
        infile = open(input_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    results: list[dict] = []
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with infile:
        reader = csv.DictReader(infile)
        for row_num, row in enumerate(reader, start=2):  # row 1 is header
            try:
                result = classify_complaint(row)
                results.append(result)
                logger.info(
                    f"Row {row_num} ({result['complaint_id']}): "
                    f"{result['category']} / {result['priority']}"
                    f"{' [NEEDS_REVIEW]' if result['flag'] else ''}"
                )
            except Exception as exc:
                logger.error(f"Row {row_num}: skipped — {exc}")
                results.append({
                    "complaint_id": row.get("complaint_id", f"ROW_{row_num}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"Classified {len(results)} complaints → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
