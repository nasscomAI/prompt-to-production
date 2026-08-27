"""
UC-0A — Complaint Classifier
Deterministic rule-based classifier implementing agents.md and skills.md.
"""
import argparse
import csv
import os
import re

csv.field_size_limit(10_000_000)

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

LOW_WORDS = ["minor", "cosmetic"]

HERITAGE_PLACE_WORDS = ["heritage", "historic", "ancient", "monument", "old city"]
HERITAGE_DAMAGE_WORDS = [
    "knocked over", "defaced", "broken", "crack", "damag",
    "removed", "not replaced", "not restored", "subsided",
    "subsidence", "sinking", "buckled", "collapsed", "caved", "upturned",
]

CATEGORY_PATTERNS = {
    "Drain Blockage": [
        r"drain\s{0,20}block", r"block\s{0,20}drain", r"\bclogged\b",
        r"\bchoked\b", r"stormwater drain", r"mosquito breeding",
    ],
    "Flooding": [
        r"\bflood", r"waterlog", r"standing water", r"\bsubmerged\b",
        r"inundat", r"waterlogg",
    ],
    "Pothole": [r"\bpothole", r"\bcrater"],
    "Streetlight": [
        r"streetlight", r"street light", r"lamp post", r"street lamp",
        r"\bunlit\b", r"\bdarkness\b", r"lights out", r"wiring theft",
        r"blackout", r"power cut", r"power outage", r"substation trip",
    ],
    "Heat Hazard": [
        r"heatwave", r"heat wave", r"\bheat\b", r"scorching", r"temperature",
        r"melting", r"bubbling", r"storing heat", r"full sun", r"\u00b0c",
        r"\bburns\b", r"\bburning\b",
    ],
    "Waste": [
        r"garbage", r"\bwaste\b", r"\btrash\b", r"litter", r"rubbish",
        r"\bdumping\b", r"dead animal", r"\boverflow", r"not cleared", r"\bpiles\b",
    ],
    "Noise": [
        r"\bnoise", r"\bmusic\b", r"\bloud\b", r"amplifier", r"\bband\b",
        r"sound system", r"drilling", r"\bidling\b",
    ],
    "Road Damage": [
        r"road damage", r"road surface", r"broken road", r"\bbuckled\b",
        r"subsided", r"subsidence", r"\bsinking\b", r"cracked",
        r"\bcollapsed\b", r"\bcaved\b", r"footpath", r"\bpaving\b",
    ],
}

COMPILED = {cat: [re.compile(p, re.IGNORECASE) for p in pats]
            for cat, pats in CATEGORY_PATTERNS.items()}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _matches(description: str, category: str) -> list:
    hits = []
    for pattern in COMPILED[category]:
        match = pattern.search(description)
        if match:
            hits.append(match.group())
    return hits


def _heritage_override(description, lowered, matched) -> bool:
    if not any(word in lowered for word in HERITAGE_PLACE_WORDS):
        return False
    blocked = {"Waste", "Noise", "Flooding", "Heat Hazard"}
    if matched & blocked:
        return False
    damage_words = any(word in lowered for word in HERITAGE_DAMAGE_WORDS)
    asset_categories = matched & {"Road Damage", "Pothole"}
    return damage_words or bool(asset_categories)


def _decide_category(description: str, lowered: str) -> tuple:
    matched = {cat for cat in CATEGORY_PATTERNS if _matches(description, cat)}
    if "Drain Blockage" in matched:
        return "Drain Blockage"
    if _heritage_override(description, lowered, matched):
        return "Heritage Damage"
    for cat in ("Heat Hazard", "Flooding", "Pothole", "Streetlight", "Waste",
                "Noise", "Road Damage"):
        if cat in matched:
            return cat
    if not description:
        return "Other"
    return "Other"


def _decide_priority(lowered: str) -> tuple:
    for keyword in SEVERITY_KEYWORDS:
        if keyword in lowered:
            return "Urgent", keyword
    for word in LOW_WORDS:
        if word in lowered:
            return "Low", word
    return "Standard", None


def _snippet(original: str, keyword: str) -> str:
    index = original.lower().find(keyword.lower())
    if index >= 0:
        return original[index:index + len(keyword)]
    return keyword


def _classify_text(complaint_id: str, description: str) -> dict:
    original = description
    lowered = description.lower()
    category = _decide_category(description, lowered)
    matched_hits = {cat: _matches(description, cat)
                    for cat in CATEGORY_PATTERNS}

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No readable description text; marked NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
        }

    hits = matched_hits.get(category, [])
    if hits:
        evidence = hits[0]
    elif category == "Heritage Damage":
        for word in HERITAGE_DAMAGE_WORDS + HERITAGE_PLACE_WORDS:
            if word in lowered:
                evidence = word
                break
        else:
            evidence = ""
    else:
        evidence = ""

    if category == "Other":
        snippet = original[:80].strip()
        reason = (f"Category not confidently assignable from '{snippet}'; "
                  f"marked NEEDS_REVIEW.")
        priority, kw = _decide_priority(lowered)
        if kw:
            reason = (f"{reason} Severity keyword '{_snippet(original, kw)}' "
                      f"present; {priority}.")
        else:
            reason = f"{reason} Priority {priority}."
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    reason = f"Classified as {category} based on '{_snippet(original, evidence)}'"
    priority, kw = _decide_priority(lowered)
    if priority == "Urgent":
        reason += f"; severity keyword '{_snippet(original, kw)}' present"
    elif priority == "Low":
        reason += f"; described as {kw}"
    reason += f"; priority {priority}."
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def classify_complaint(row: dict) -> dict:
    row = row or {}
    complaint_id = str(row.get("complaint_id") or "").strip()
    description = str(row.get("description") or "").strip()
    return _classify_text(complaint_id, description)


def batch_classify(input_path: str, output_path: str):
    if not os.path.isfile(input_path):
        raise SystemExit(f"Error: input file not found: {input_path}")
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as exc:
        raise SystemExit(f"Error: cannot read input file: {exc}")

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": str(row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row failed during processing; marked NEEDS_REVIEW.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")