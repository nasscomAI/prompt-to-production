"""
UC-0A — Complaint Classifier

Deterministic rule-based classifier that enforces the contracts in agents.md:
  - Category ∈ {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
                Heritage Damage, Heat Hazard, Drain Blockage, Other}
  - Priority ∈ {Urgent, Standard, Low}
  - Urgent is triggered by any severity keyword
    (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)
  - reason cites specific tokens from description
  - flag ∈ {"NEEDS_REVIEW", ""}
"""
import argparse
import csv
import re
import sys
from typing import Dict, List, Tuple

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Pothole":         ["pothole", "potholes"],
    "Flooding":        ["flood", "flooded", "flooding", "waterlogged", "waterlogging",
                        "knee-deep", "knee deep", "submerged", "inundated", "standing water",
                        "rainwater"],
    "Streetlight":     ["streetlight", "street light", "street-light", "lamppost",
                        "lamp post", "light pole", "dark stretch", "no light",
                        "lights not working", "bulb", "not lit",
                        "unlit", "darkness", "substation"],
    "Waste":           ["garbage", "trash", "refuse", "rubbish", "litter",
                        "dustbin", "dump", "dumping", "solid waste",
                        "dead animal", "carcass",
                        "waste bin", "waste bins", "trash bin", "overflowing", "overflow",
                        "waste not", "waste piles", "market waste"],
    "Noise":           ["noise", "loudspeaker", "honking", "blaring",
                        "sound pollution", "decibel", "loud music",
                        "playing music", "music past", "past midnight",
                        "music", "band playing", "drilling", "idling"],
    "Road Damage":     ["cracked road", "broken road", "damaged road", "road surface",
                        "tar peeling", "road cave", "sinking road", "road collapse",
                        "crumbling road", "road erosion",
                        "footpath", "pavement", "tiles broken", "broken tiles", "upturned",
                        "subsided", "cobblestones"],
    "Heritage Damage": ["heritage", "monument", "historical", "fort wall", "temple wall",
                        "statue", "shrine", "old structure", "protected site"],
    "Heat Hazard":     ["heatwave", "heat wave", "heatstroke", "sunstroke",
                        "dehydration", "no shade", "shelter needed", "extreme heat",
                        "44°c", "45°c", "46°c", "47°c", "48°c", "49°c", "50°c", "51°c", "52°c",
                        "melting", "unbearable", "burns on contact", "full sun",
                        "dangerous temperatures", "storing heat", "surface temperature"],
    "Drain Blockage":  ["drain", "sewer", "gutter", "choked", "blocked drain",
                        "manhole", "sewage", "drainage"],
}

LOW_PRIORITY_HINTS = ["minor", "small", "occasional", "cosmetic", "slight"]


def _find_matches(text: str, keywords: List[str]) -> List[str]:
    """Return keywords found in text as whole words / substrings (case-insensitive)."""
    hits = []
    lowered = text.lower()
    for kw in keywords:
        if " " in kw or "-" in kw:
            if kw in lowered:
                hits.append(kw)
        else:
            if re.search(rf"\b{re.escape(kw)}\w*", lowered):
                hits.append(kw)
    return hits


def _detect_category(description: str) -> Tuple[str, List[str], bool]:
    """
    Returns (category, matched_tokens, ambiguous).
    ambiguous=True when two or more categories have matches.
    """
    scores: Dict[str, List[str]] = {}
    for category, kws in CATEGORY_KEYWORDS.items():
        hits = _find_matches(description, kws)
        if hits:
            scores[category] = hits

    if not scores:
        return "Other", [], False

    ranked = sorted(scores.items(), key=lambda kv: (-len(kv[1]), ALLOWED_CATEGORIES.index(kv[0])))
    top_category, top_hits = ranked[0]
    ambiguous = len(ranked) >= 2 and len(ranked[1][1]) == len(top_hits)
    return top_category, top_hits, ambiguous


def _detect_priority(description: str) -> Tuple[str, List[str]]:
    """Returns (priority, severity_matches). Urgent overrides everything."""
    severity_hits = _find_matches(description, SEVERITY_KEYWORDS)
    if severity_hits:
        return "Urgent", severity_hits
    if _find_matches(description, LOW_PRIORITY_HINTS):
        return "Low", []
    return "Standard", []


def _build_reason(category: str, cat_hits: List[str],
                  priority: str, sev_hits: List[str],
                  ambiguous: bool) -> str:
    parts = []
    if cat_hits:
        parts.append(f"{category} inferred from '{', '.join(cat_hits)}'")
    else:
        parts.append(f"{category} assigned: no category keywords matched")
    if priority == "Urgent" and sev_hits:
        parts.append(f"marked Urgent due to severity term '{', '.join(sev_hits)}'")
    elif priority == "Low":
        parts.append("marked Low due to minor-severity language")
    else:
        parts.append("priority Standard (no severity term present)")
    if ambiguous:
        parts.append("flagged for review due to competing category signals")
    return "; ".join(parts) + "."


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, cat_hits, ambiguous = _detect_category(description)
    priority, sev_hits = _detect_priority(description)

    flag = ""
    if category == "Other" or ambiguous:
        flag = "NEEDS_REVIEW"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ("Urgent", "Standard", "Low"):
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _build_reason(category, cat_hits, priority, sev_hits, ambiguous),
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write results CSV."""
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        infile = open(input_path, "r", encoding="utf-8", newline="")
    except FileNotFoundError:
        raise

    with infile, open(output_path, "w", encoding="utf-8", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row.get("complaint_id") or f"ROW_{i}").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be classified due to parse error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}", file=sys.stdout)
