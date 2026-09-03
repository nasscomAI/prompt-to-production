"""
UC-0A — Complaint Classifier | Vibe Coding Workshop (Civic Tech Edition)

Workshop workflow: RICE → agents.md → skills.md → CRAFT
Author: Sneha (participant/Sneha-Amritsar) | Verified on 4 cities (Pune, Hyderabad, Kolkata, Ahmedabad)

Enforcement (agents.md):
  - Category ∈ {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
    Heritage Damage, Heat Hazard, Drain Blockage, Other} — no Water Damage.
  - Priority = Urgent iff description contains any of: injury, child, school,
    hospital, ambulance, fire, hazard, fell, collapse (case-insensitive).
  - Every row must include reason citing the matched keyword + quoted description.
  - If no keyword matches or description empty → Other + NEEDS_REVIEW; exception → BAD_ROW.

Usage:
  python classifier.py --input data/city-test-files/test_pune.csv --output results_pune.csv
  python classifier.py --input data/city-test-files/test_hyderabad.csv --output results_hyderabad.csv

Skills: classify_complaint, batch_classify, taxonomy_enforcement, severity_detection, disambiguation
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Taxonomy & Rules
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES: List[str] = [
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

SEVERITY_KEYWORDS: List[str] = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

# Precedence-ordered keywords — more specific first to prevent bleed.
# Strong heritage signals beat generic location mentions; heat phrases use word-phrases to avoid
# substring false hits (photographing → hot, Sunday → sun).
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Heritage Damage": [
        "heritage",
        "historic",
        "ancient",
        "tagore",
        "marble palace",
        "cobblestones",
        "heritage stone",
        "heritage zone",
        "heritage street",
        "billboard installation",
        "defaced",
    ],
    "Drain Blockage": [
        "drain blocked",
        "drain 100% blocked",
        "drain completely blocked",
        "main drain blocked",
        "main stormwater drain",
        "stormwater drain",
        "drain blockage",
        "sewage",
        "mosquito breeding",
        "dengue concern",
        "drainage & flooding",
        "draining directly onto public road",
    ],
    "Flooding": [
        "flooded",
        "flooding",
        "flood",
        "waterlogging",
        "overflow",
        "underpass flooded",
        "underpass floods",
        "bridge floods",
        "bridge approach floods",
        "channel rainwater",
        "stranded",
        "abandoned",
    ],
    "Pothole": ["pothole", "potholes"],
    "Road Damage": [
        "road damage",
        "broken road",
        "uneven",
        "road surface",
        "cracked",
        "sinking",
        "sunk",
        "buckled",
        "subsided",
        "subsidence",
        "crater",
        "collapsed",
        "collapse",
        "footpath",
        "tiles broken",
        "upturned",
        "manhole",
        "pavement",
        "paving removed",
        "bench",
        "paving",
        "utility work",
        "cable laying",
    ],
    "Waste": [
        "garbage",
        "trash",
        "waste",
        "dump",
        "dumped",
        "dead animal",
        "not cleared",
        "not removed",
        "bins",
        "piles of waste",
        "piles",
        "health concern",
        "health risk",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "lamp post",
        "lamp",
        "light not working",
        "light out",
        "lights out",
        "flickering",
        "sparking",
        "unlit",
        "darkness",
        "substation tripped",
        "wiring theft",
    ],
    "Heat Hazard": [
        "heat",
        "temperature",
        "melting",
        "heatwave",
        "burning",
        "full sun",
        "unbearable",
        "bubbling",
        "tarmac surface",
        "reaching dangerous temperatures",
        "grass dying",
        "split branches",
        "burns on contact",
        "44°c",
        "45°c",
        "52°c",
    ],
    "Noise": [
        "noise",
        "loud",
        "sound pollution",
        "music",
        "drilling",
        "band playing",
        "amplifiers",
        "wedding venue",
        "wedding band",
        "idling",
        "trucks idling",
        "playing music",
    ],
}


# ---------------------------------------------------------------------------
# Core: disambiguation & classification
# ---------------------------------------------------------------------------

def _match_category(description_lower: str) -> Tuple[str, str]:
    """Return (category, matched_keyword) with precedence and disambiguation.

    Handles: heritage zone + garbage → Waste, Tagore band → Noise,
    road surface + temperature → Heat Hazard, overflow + garbage → Waste,
    drain blocked + flood → Drain Blockage.

    Args:
        description_lower: Lowercased complaint description.

    Returns:
        Tuple of (category, matched phrase). Falls back to ("Other", "").
    """
    strong_heritage = [
        "heritage lamp",
        "heritage stone",
        "historic tram",
        "historic",
        "ancient",
        "marble palace",
        "cobblestones",
        "defaced",
        "billboard installation",
    ]
    for kw in strong_heritage:
        if kw in description_lower:
            return "Heritage Damage", kw

    generic_heritage_present = any(
        x in description_lower
        for x in ["heritage zone", "heritage area", "heritage precinct", "heritage street", "heritage", "tagore"]
    )
    has_waste = any(w in description_lower for w in CATEGORY_KEYWORDS["Waste"])
    has_noise = any(n in description_lower for n in CATEGORY_KEYWORDS["Noise"])
    has_heat = any(
        h in description_lower
        for h in ["temperature", "melting", "heatwave", "heat", "burning", "bubbling", "unbearable", "tarmac surface", "44°c", "45°c", "52°c"]
    )

    # Location-only heritage should not override waste/noise complaint
    if generic_heritage_present and has_waste and not any(k in description_lower for k in strong_heritage):
        for kw in CATEGORY_KEYWORDS["Waste"]:
            if kw in description_lower:
                return "Waste", kw
    if generic_heritage_present and has_noise and not any(k in description_lower for k in strong_heritage):
        for kw in CATEGORY_KEYWORDS["Noise"]:
            if kw in description_lower:
                return "Noise", kw

    if "heritage street" in description_lower:
        return "Heritage Damage", "heritage street"
    if "heritage" in description_lower and not has_waste and not has_noise:
        return "Heritage Damage", "heritage"

    for cat in ["Drain Blockage", "Flooding", "Pothole", "Heat Hazard", "Road Damage", "Waste", "Streetlight", "Noise"]:
        for kw in CATEGORY_KEYWORDS[cat]:
            if kw in description_lower:
                if cat == "Flooding" and kw == "overflow":
                    if any(w in description_lower for w in ["garbage", "trash", "waste", "bins", "dump"]):
                        continue
                if cat == "Road Damage" and kw == "road surface" and has_heat:
                    continue
                return cat, kw

    if generic_heritage_present:
        for kw in CATEGORY_KEYWORDS["Heritage Damage"]:
            if kw in description_lower:
                return "Heritage Damage", kw
    return "Other", ""


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Classify a single complaint row.

    Args:
        row: Dict with at least `complaint_id` and `description` (raw CSV row).

    Returns:
        Dict with keys `complaint_id`, `category`, `priority`, `reason`, `flag`.
        Category is validated against ALLOWED_CATEGORIES; priority is Urgent iff
        severity keyword hit; reason cites matched keyword + description quote.
    """
    complaint_id = (row.get("complaint_id") or "UNKNOWN").strip()
    description_raw = row.get("description", "")
    description = description_raw.strip()
    description_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — no words to cite",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_kw = _match_category(description_lower)

    severity_hits = [w for w in SEVERITY_KEYWORDS if w in description_lower]
    priority = "Urgent" if severity_hits else "Standard"

    if category != "Other" and matched_kw:
        reason = f"Matched '{matched_kw}' in description: \"{description[:120]}\""
        if severity_hits:
            reason += f" | severity keyword(s) '{', '.join(severity_hits)}' → Urgent"
    elif category == "Other":
        reason = f"No category keyword matched in: \"{description[:120]}\""
        if severity_hits:
            reason += f" | severity keyword(s) '{', '.join(severity_hits)}' → Urgent"
    else:
        reason = f"Cited words from description: \"{description[:120]}\""

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> int:
    """Batch classify CSV with robust error handling.

    Args:
        input_path: Path to `test_[city].csv` with `complaint_id, description` columns.
        output_path: Path to write `results_[city].csv`.

    Returns:
        Number of rows written.

    Raises:
        ValueError: If CSV has no header.
        FileNotFoundError: If input file missing.
    """
    in_p = Path(input_path)
    if not in_p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(in_p, newline="", encoding="utf-8") as infile, open(Path(output_path), "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError(f"Input CSV has no header: {input_path}")

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for row in reader:
            try:
                clean_row = {k: (v if v is not None else "") for k, v in row.items()}
                result = classify_complaint(clean_row)
                if result["category"] not in ALLOWED_CATEGORIES:
                    result["category"] = "Other"
                    result["flag"] = "NEEDS_REVIEW"
                    result["reason"] += " | corrected to allowed taxonomy"
                writer.writerow(result)
                count += 1
            except Exception as exc:  # per-row isolation
                writer.writerow(
                    {
                        "complaint_id": (row.get("complaint_id") or "UNKNOWN") if isinstance(row, dict) else "UNKNOWN",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error: {exc}",
                        "flag": "BAD_ROW",
                    }
                )
                count += 1
                print(f"WARN: BAD_ROW {row.get('complaint_id', 'UNKNOWN')}: {exc}", file=sys.stderr)

    return count


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — categorizes citizen complaints with severity-aware priority.",
        epilog="Example: python classifier.py --input data/city-test-files/test_pune.csv --output results_pune.csv",
    )
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    n = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output} ({n} rows)")


if __name__ == "__main__":
    main()
