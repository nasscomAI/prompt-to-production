"""
UC-0A — Complaint Classifier
Deterministic rule-based classifier implementing the contracts in agents.md and skills.md.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

MINIMIZER_WORDS = ["minor", "cosmetic"]

HERITAGE_WORDS = ["heritage", "historic", "monument"]
HERITAGE_DAMAGE_WORDS = [
    "knocked over", "defaced", "broken", "crack", "damag",
    "vandal", "not replaced", "not restored", "removed", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlog", "water logg", "inundat", "submerged", "standing water"],
    "Streetlight": [
        "streetlight", "street light", "lamp post", "street lamp",
        "power cut", "power outage", "blackout", "no electricity", "darkness",
        "unlit", "lights out",
    ],
    "Waste": ["garbage", "waste", "trash", "litter", "rubbish", "dumping", "dead animal"],
    "Noise": ["noise", "loud", "amplifier", "sound system", "band play", "music", "drilling"],
    "Heat Hazard": ["heatwave", "heat wave", "extreme heat", "scorching", "temperature", "melting", "bubbling", "storing heat", "full sun"],
    "Drain Blockage": ["drain block", "blocked drain", "clogged", "choked", "overflowing drain", "stormwater drain"],
    "Road Damage": [
        "road damage", "footpath", "broken road", "buckled",
        "subsided", "subsidence", "sinking", "caved", "upturned paving",
    ],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _original_snippets(description: str, lowered: str, patterns: list) -> list:
    snippets = []
    for pattern in patterns:
        index = lowered.find(pattern)
        if index >= 0:
            snippets.append(description[index:index + len(pattern)])
    return snippets


def _severity_hits(lowered: str, description: str) -> list:
    hits = []
    for keyword in SEVERITY_KEYWORDS:
        match = re.search(rf"\b{re.escape(keyword)}\b", description, flags=re.IGNORECASE)
        if match:
            hits.append(match.group())
    return hits


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    row = row or {}
    description = str(row.get("description") or "").strip()
    complaint_id = row.get("complaint_id") or ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No readable description text was available to base a classification on.",
            "flag": "NEEDS_REVIEW",
        }

    lowered = description.lower()
    severity_matches = _severity_hits(lowered, description)

    heritage_words = [w for w in HERITAGE_WORDS if w in lowered]
    heritage_damage = [d for d in HERITAGE_DAMAGE_WORDS if d in lowered]

    scores = {}
    evidence = {}
    for category, patterns in CATEGORY_KEYWORDS.items():
        present = [p for p in patterns if p in lowered]
        if present:
            scores[category] = len(present)
            evidence[category] = _original_snippets(description, lowered, present)

    flag = ""
    if not scores:
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence[category] = [description.strip().rstrip(".")]
    else:
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_score = ranked[0][1]
        tied = [name for name, score in ranked if score == top_score]
        if len(tied) > 1:
            category = min(tied, key=CATEGORIES.index)
            flag = "NEEDS_REVIEW"
        else:
            category = ranked[0][0]

    if heritage_words and heritage_damage and category != "Heritage Damage":
        category = "Heritage Damage"
        evidence[category] = _original_snippets(
            description, lowered, heritage_words + heritage_damage
        )

    if severity_matches:
        priority = "Urgent"
    elif any(word in lowered for word in MINIMIZER_WORDS):
        priority = "Low"
    else:
        priority = "Standard"

    citations = ", ".join(f"'{quote}'" for quote in evidence.get(category, [])[:3])
    reason = f"Classified as {category} based on {citations}; priority {priority}"
    if severity_matches:
        reason += f" due to severity word(s) {', '.join(severity_matches)}"
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
    Malformed rows become Other/NEEDS_REVIEW entries; the output file is always written.
    """
    with open(input_path, newline="", encoding="utf-8") as infile, \
            open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row or {}).get("complaint_id") or "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be processed: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
