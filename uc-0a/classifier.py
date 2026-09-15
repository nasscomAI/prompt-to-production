"""
UC-0A — Complaint Classifier
Rule-based classifier enforced by uc-0a/agents.md and uc-0a/skills.md:
category, priority, reason, flag from a free-text civic complaint description.
"""
import argparse
import csv
import re
from collections import Counter

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

URGENT_KEYWORDS = [
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


def _p(pattern: str):
    return re.compile(pattern, re.IGNORECASE)


PATTERNS = [
    (_p(r"\bpothole"), "Pothole", 1),
    (_p(r"\bflood"), "Flooding", 1),
    (_p(r"\bwaterlogged"), "Flooding", 1),
    (_p(r"\bsubmerged"), "Flooding", 1),
    (_p(r"\brainwater\b"), "Flooding", 0.5),
    (_p(r"\brain\b"), "Flooding", 0.5),
    (_p(r"\bstanding in water"), "Flooding", 0.5),
    (_p(r"\bstreetlight"), "Streetlight", 1),
    (_p(r"\blight"), "Streetlight", 1),
    (_p(r"\blamp"), "Streetlight", 1),
    (_p(r"\bunlit"), "Streetlight", 1),
    (_p(r"\bsubstation"), "Streetlight", 1),
    (_p(r"\bdark"), "Streetlight", 1),
    (_p(r"\bgarbage"), "Waste", 1),
    (_p(r"\bwaste"), "Waste", 1),
    (_p(r"\bbins"), "Waste", 1),
    (_p(r"\bdead animal"), "Waste", 1),
    (_p(r"\brubbish"), "Waste", 1),
    (_p(r"\brefuse"), "Waste", 1),
    (_p(r"\bmusic"), "Noise", 1),
    (_p(r"\bnoise"), "Noise", 1),
    (_p(r"\bdrilling"), "Noise", 1),
    (_p(r"\bamplifier"), "Noise", 1),
    (_p(r"\bband\b"), "Noise", 1),
    (_p(r"\bidling"), "Noise", 1),
    (_p(r"\broad surface"), "Road Damage", 1),
    (_p(r"\bcracked"), "Road Damage", 1),
    (_p(r"\bsinking"), "Road Damage", 1),
    (_p(r"\bsubsided\b"), "Road Damage", 1),
    (_p(r"\bsubsidenc"), "Road Damage", 1),
    (_p(r"\bcollapsed\b"), "Road Damage", 1),
    (_p(r"\bmanhole"), "Road Damage", 1),
    (_p(r"\bfootpath"), "Road Damage", 1),
    (_p(r"\bpaving"), "Road Damage", 1),
    (_p(r"\bbuckled"), "Road Damage", 1),
    (_p(r"\bcrater"), "Road Damage", 1),
    (_p(r"\bcobblestone"), "Road Damage", 1),
    (_p(r"\bdrain"), "Drain Blockage", 1),
    (_p(r"\bblocked"), "Drain Blockage", 1),
    (_p(r"\bblockage"), "Drain Blockage", 1),
    (_p(r"\bstormwater"), "Drain Blockage", 1),
    (_p(r"\bsewer"), "Drain Blockage", 1),
    (_p(r"\bmelting"), "Heat Hazard", 1),
    (_p(r"\bbubbling"), "Heat Hazard", 1),
    (_p(r"\bheatwave"), "Heat Hazard", 1),
    (_p(r"\bheat\b"), "Heat Hazard", 1),
    (_p(r"\btemperature"), "Heat Hazard", 1),
    (_p(r"\bburn"), "Heat Hazard", 1),
    (_p(r"\bdefaced"), "Heritage Damage", 1),
    (_p(r"\bknocked over"), "Heritage Damage", 1),
    (_p(r"\bheritage stone"), "Heritage Damage", 1),
    (_p(r"\bcobblestone"), "Heritage Damage", 1),
    (_p(r"\bheritage\b"), "Heritage Damage", 0.5),
    (_p(r"\bhistoric"), "Heritage Damage", 0.5),
    (_p(r"\bancient"), "Heritage Damage", 0.5),
    (_p(r"\bmuseum"), "Heritage Damage", 0.5),
]

TEMP_PATTERN = _p(r"\d+\s?°[cC]")
SUN_PATTERN = _p(r"\bsun\b")

ACTIVE_FLOOD_WORDS = (
    _p(r"\bflooded"),
    _p(r"\bfloods\b"),
    _p(r"\bwaterlogged"),
    _p(r"\bsubmerged"),
    _p(r"\bstanding in water"),
)


def _detect_category(description: str):
    scores = Counter()
    cited = []
    active_flood = any(pat.search(description) for pat in ACTIVE_FLOOD_WORDS)
    has_drain = _p(r"\bdrain\b").search(description) or _p(r"\bblocked\b").search(description)

    dual_flood_drain = active_flood and has_drain
    if dual_flood_drain:
        return "Flooding", ["flooded", "drain"], True

    for pattern, category, weight in PATTERNS:
        match = pattern.search(description)
        if match:
            scores[category] += weight
            cited.append(match.group(0))

    temp_match = TEMP_PATTERN.search(description)
    if temp_match:
        scores["Heat Hazard"] += 1
        cited.append(temp_match.group(0))
    sun_match = SUN_PATTERN.search(description)
    if sun_match:
        scores["Heat Hazard"] += 1
        cited.append(sun_match.group(0))

    if not scores:
        return "Other", [], True

    top_score = max(scores.values())
    top = [c for c in sorted(CATEGORIES, key=CATEGORIES.index) if scores.get(c) == top_score]

    if len(top) > 1:
        return top[0], cited, True

    return top[0], cited, False


def _priority(description: str) -> str:
    text = description.lower()
    if any(keyword in text for keyword in URGENT_KEYWORDS):
        return "Urgent"
    return "Standard"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty; category could not be determined.",
            "flag": "NEEDS_REVIEW",
        }

    priority = _priority(description)
    category, cited, needs_review = _detect_category(description)

    unique_cited = list(dict.fromkeys(cited))[:4]
    quoted = ", ".join('"' + word + '"' for word in unique_cited)
    if quoted:
        reason = (f"Classified as {category}: cited words from description — {quoted}.")
    else:
        reason = f"Classified as {category}: no specific category words found in description."
    if needs_review:
        reason = reason + f" Ambiguous — flagged NEEDS_REVIEW."
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = list(reader.fieldnames) if reader.fieldnames else []
        rows = list(reader)

    out_headers = headers + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_headers)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be processed — flagged NEEDS_REVIEW.",
                    "flag": "NEEDS_REVIEW",
                }
            out.update(result)
            writer.writerow(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")