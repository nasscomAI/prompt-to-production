"""
UC-0A — Complaint Classifier

Deterministic civic-complaint classifier built to the enforcement rules in
agents.md and the skill contracts in skills.md.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv
import sys

# --- Fixed schema (agents.md enforcement) -----------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST force priority = Urgent (case-insensitive substring).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

# Category detection is ordered: the first rule that matches wins, so more
# distinctive/root-cause categories are checked before broader ones. Only the
# `description` text is used (never ward, location, reporter, etc.).
#
# Ordering rationale:
#   Heat Hazard first  — temperature-driven issues (melting/bubbling roads at 44°C)
#                        are the distinctive signal in heat-affected cities.
#   Drain Blockage     — treated as root cause when a drain is blocked, even if
#                        the symptom described is flooding.
#   Flooding           — water on the ground without a stated blockage.
#   Heritage Damage    — explicit heritage context.
#   Streetlight        — lighting/darkness/power-to-lights issues.
#   Pothole / Road Damage / Waste / Noise — general physical categories.

HEAT_KEYWORDS = [
    "°c", "℃", "degrees", "melting", "heatwave", "heat wave", "storing heat",
    "sunstroke", "temperature", "burns on contact", "bubbling", "full sun",
    "dangerous temperature", "heat",
]
FLOODING_KEYWORDS = [
    "flood", "waterlogg", "water-logg", "water logg", "knee-deep", "knee deep",
    "standing in water", "submerged",
]
STREETLIGHT_KEYWORDS = [
    "streetlight", "street light", "lights out", "light out", "lamp",
    "flickering", "unlit", "darkness", "dark after", "dark at night",
    "substation tripped", "substation", "lamp post",
]
ROAD_DAMAGE_KEYWORDS = [
    "road surface", "surface buckled", "buckled", "cracked", "sinking",
    "subside", "subsided", "collapsed", "road collapse", "crater", "paving",
    "cobblestone", "footpath", "sinkhole", "broken road", "tiles broken",
    "road caved", "road subsidence",
]
WASTE_KEYWORDS = [
    "garbage", "waste", "trash", "dead animal", "dump", "dumped", "bins",
    "litter", "refuse", "overflow",
]
NOISE_KEYWORDS = [
    "noise", "loud", "music", "band playing", "amplifier", "drilling",
    "idling", "loudspeaker",
]


# --- Skill: classify_complaint ----------------------------------------------

def _match_category(description_lower: str):
    """Return the first matching category for the description, else None (ambiguous)."""
    d = description_lower

    # Heat Hazard — temperature / heat-driven damage.
    if any(k in d for k in HEAT_KEYWORDS):
        return "Heat Hazard"

    # Drain Blockage — a blocked drain/manhole/sewer, treated as root cause.
    if ("drain" in d and "block" in d) or any(k in d for k in ["manhole", "sewer", "stormwater"]):
        return "Drain Blockage"

    # Flooding — water on the ground with no stated blockage.
    if any(k in d for k in FLOODING_KEYWORDS):
        return "Flooding"

    # Heritage Damage — explicit heritage context.
    if "heritage" in d:
        return "Heritage Damage"

    # Streetlight — lighting / darkness / power-to-lights.
    if any(k in d for k in STREETLIGHT_KEYWORDS):
        return "Streetlight"

    # Pothole.
    if "pothole" in d:
        return "Pothole"

    # Road Damage — surface/structure damage.
    if any(k in d for k in ROAD_DAMAGE_KEYWORDS):
        return "Road Damage"

    # Waste.
    if any(k in d for k in WASTE_KEYWORDS):
        return "Waste"

    # Noise.
    if any(k in d for k in NOISE_KEYWORDS):
        return "Noise"

    return None


def _found_severity_keywords(description_lower: str):
    """Return the list of severity keywords present in the description."""
    return [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Uses ONLY the `description` field (plus `complaint_id` for identity).
    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    Never raises on a single row.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    # Null / missing description -> flag, do not guess.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was missing or empty; classification could not be determined.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # Category (first-match wins; None -> ambiguous).
    category = _match_category(description_lower)
    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority: Urgent if any severity keyword present, else Standard.
    severity_hits = _found_severity_keywords(description_lower)
    priority = "Urgent" if severity_hits else "Standard"

    # Reason: one sentence citing specific words from the description.
    if severity_hits:
        cited = ", ".join(f"'{kw}'" for kw in severity_hits)
        reason = f"Classified as {category}; marked Urgent due to severity term(s): {cited}."
    elif flag == "NEEDS_REVIEW":
        snippet = description[:60].rstrip()
        reason = f"Complaint type ambiguous from description ('{snippet}...'); needs manual review."
    else:
        snippet = description.split(".")[0].strip()[:80]
        reason = f"Classified as {category} based on description: '{snippet}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# --- Skill: batch_classify --------------------------------------------------

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.

    Every input row yields exactly one output row. A per-row failure is caught
    and written as an Other / NEEDS_REVIEW result rather than crashing the run.
    Fails fast with a clear message if the input file cannot be opened.
    """
    try:
        infile = open(input_path, "r", newline="", encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: could not open input file '{input_path}': {exc}", file=sys.stderr)
        raise SystemExit(1)

    processed = 0
    flagged = 0
    with infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never crash the batch on a bad row
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be classified due to an error: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)
            processed += 1
            if result["flag"] == "NEEDS_REVIEW":
                flagged += 1

    print(f"Processed {processed} row(s); {flagged} flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
