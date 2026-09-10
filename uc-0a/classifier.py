"""
UC-0A — Complaint Classifier
Rule-based implementation driven by agents.md / skills.md.
Closed taxonomy, severity override, quoted reason, NEEDS_REVIEW flag.
Description-only: ward / reporter / days_open / city never influence output.
"""
import argparse
import csv
import os
import re
import sys

CATEGORIES = [
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

# Severity override: substring match on lowercased description.
# Stems ("injur", "hospit", "collaps") cover injury/injured, hospital/hospitalised,
# collapse/collapsed while still triggering on every README keyword.
SEVERITY_SUBSTRINGS = (
    "injur",      # injury, injured, injuries
    "child",      # child, children
    "school",
    "hospit",     # hospital, hospitalised
    "ambulance",
    "fire",
    "hazard",     # hazard, hazardous
    "fell",
    "collaps",    # collapse, collapsed
)

HERITAGE_MARKERS = (
    "heritage", "historic", "museum", "palace", "monument",
    "step well", "stepwell", "tram", "cobblestone", "precinct",
    "tagore", "victoria", "marble palace", "old city",
)

HERITAGE_DAMAGE_VERBS = (
    "knocked over", "broken up", "broken", "defaced", "damaged",
    "destroyed", "not restored", "not replaced", "removed",
    "vandal", "cable laying", "billboard",
)

HEAT_SIGNALS = (
    "melting", "44", "45", "52", "°c", "degrees", "temperature",
    "temperatures", "heatwave", "heat", "burns", "unbearable",
    "sticking", "bubbling", "full sun",
)

FLOOD_SIGNALS = (
    "flooded", "flooding", "floods", "knee-deep", "knee deep",
    "stranded", "standing in water", "abandoned", "inaccessible",
)

# Standing water proof (flooding-risk-only phrases like "flooding risk"
# without any of these must fall through to Drain Blockage).
FLOOD_PROOF_SIGNALS = (
    "flooded", "knee-deep", "knee deep",
    "stranded", "standing in water", "abandoned", "inaccessible",
)

DRAIN_SIGNALS = (
    "drain blocked", "drain completely blocked", "drain 100% blocked",
    "blocked drain", "blocked with", "stormwater drain",
    "main drain blocked", "mosquito", "dengue", "debris",
)

POTHOLE_SIGNALS = (
    "pothole", "potholes", "tyre damage", "tire damage",
    "tyre blowout", "tyre blowouts", "blowout", "wheel swallowed",
    "motorcycle wheel",
)

ROAD_DAMAGE_SIGNALS = (
    "cracked", "crack", "sinking", "subsided", "subsidence",
    "buckled", "collapsed surface", "crater", "broken footpath",
    "footpath tiles broken", "footpath broken", "tiles broken",
    "upturned paving", "upturned", "broken bench", "manhole",
    "missing cover", "cover missing", "utility work", "gas pipeline",
)

STREETLIGHT_SIGNALS = (
    "streetlight", "streetlights", "street light", "lights out",
    "light out", "unlit", "flickering", "sparking", "darkness",
    "dark at night", "very dark", "substation tripped",
)

WASTE_SIGNALS = (
    "garbage", "waste", "overflowing", "overflow", "bins",
    "dead animal", "dumped", "piles of waste", "piles",
    "not cleared", "not removed", "market waste",
)

NOISE_SIGNALS = (
    "music", "wedding", "band playing", "drilling", "amplifier",
    "amplifiers", "club music", "idling", "midnight", "2am", "5am",
    "noise",
)


def _contains(text: str, phrases) -> bool:
    return any(p in text for p in phrases)


def _has_heritage_damage(desc: str) -> bool:
    if not _contains(desc, HERITAGE_MARKERS):
        return False
    # Physical damage to a heritage asset must be explicit.
    # Normal faults (lights out, garbage, amplifiers) in a heritage area do NOT count.
    if _contains(desc, ("lights out", "garbage", "waste", "amplifier", "band playing", "music")) \
            and not _contains(desc, HERITAGE_DAMAGE_VERBS):
        return False
    return _contains(desc, HERITAGE_DAMAGE_VERBS)


def _quote_phrase(description: str) -> str:
    """Return 2+ consecutive words actually present in the description."""
    text = (description or "").strip()
    if not text:
        return ""
    # Prefer the first meaningful clause (up to 6 words) without sentence breaks.
    words = re.findall(r"[A-Za-z0-9°/%-]+", text)
    words = [w.strip(".-") for w in words]
    words = [w for w in words if w]
    if len(words) >= 4:
        return " ".join(words[:4])
    if len(words) >= 2:
        return " ".join(words)
    return text


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id") or "").strip()
    description = row.get("description") or ""
    location = row.get("location") or ""
    desc = description.strip()
    low = desc.lower()

    # --- error_handling: null / empty / vague -> Other + NEEDS_REVIEW, never throw ---
    if not desc:
        fallback_quote = _quote_phrase(location) or "no description"
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": f"Classified as Other due to missing description ('{fallback_quote}').",
            "flag": "NEEDS_REVIEW",
        }

    # --- category precedence (description-only) ---
    has_flood = _contains(low, FLOOD_SIGNALS)
    if has_flood and "risk" in low and not _contains(low, FLOOD_PROOF_SIGNALS):
        # Flooding-risk-only (e.g. "at flooding risk") with no standing
        # water yet -> not Flooding; Drain Blockage handles it below.
        has_flood = False
    has_drain = _contains(low, DRAIN_SIGNALS)
    has_heritage_marker = _contains(low, HERITAGE_MARKERS)

    if _has_heritage_damage(low):
        category = "Heritage Damage"
    elif _contains(low, HEAT_SIGNALS):
        category = "Heat Hazard"
    elif has_flood:
        category = "Flooding"
    elif has_drain:
        category = "Drain Blockage"
    elif _contains(low, POTHOLE_SIGNALS):
        category = "Pothole"
    elif _contains(low, ROAD_DAMAGE_SIGNALS):
        category = "Road Damage"
    elif _contains(low, STREETLIGHT_SIGNALS):
        category = "Streetlight"
    elif _contains(low, WASTE_SIGNALS):
        category = "Waste"
    elif _contains(low, NOISE_SIGNALS):
        category = "Noise"
    else:
        category = "Other"

    # --- priority: severity override on description text only ---
    priority = "Urgent" if any(s in low for s in SEVERITY_SUBSTRINGS) else "Standard"

    # --- flag: NEEDS_REVIEW on genuine ambiguity ---
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif has_flood and has_drain:
        # Standing water + blocked drain with no clear primary symptom.
        flag = "NEEDS_REVIEW"
    elif has_heritage_marker and category != "Heritage Damage":
        # Heritage-area symptom with no physical damage to a heritage asset.
        flag = "NEEDS_REVIEW"

    # --- reason: one sentence quoting 2+ consecutive words from THIS description ---
    phrase = _quote_phrase(desc).replace(".", "")
    reason = f"Classified as {category} due to '{phrase}' in the description."
    # Guarantee a single sentence (strip stray periods inside the quote tail).
    reason = reason.strip()
    if not reason.endswith("."):
        reason += "."

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
    Never crashes on bad rows; always produces output.
    """
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        input_rows = list(reader)

    results = []
    for i, row in enumerate(input_rows):
        try:
            if row.get("complaint_id") is None or str(row.get("complaint_id")).strip() == "":
                row = dict(row)
                row["complaint_id"] = f"ROW-{i + 1}"
                print(f"Warning: missing complaint_id at row {i + 1}, using ROW-{i + 1}",
                      file=sys.stderr)
            results.append(classify_complaint(row))
        except Exception as e:  # never crash: map failures to Other/NEEDS_REVIEW
            print(f"Warning: failed to classify row {i + 1}: {e}", file=sys.stderr)
            desc = (row.get("description") or "") if isinstance(row, dict) else ""
            phrase = (_quote_phrase(desc) or "unclassifiable row").replace(".", "")
            results.append({
                "complaint_id": str((row.get("complaint_id") if isinstance(row, dict) else "") or f"ROW-{i + 1}"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classified as Other due to '{phrase}' in the description.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
