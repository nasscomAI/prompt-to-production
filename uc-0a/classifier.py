"""
UC-0A — Complaint Classifier

Implements the enforcement rules in agents.md:
  - category is exactly one of the allowed list
  - priority is Urgent when a severity keyword appears
  - every row gets a one-sentence reason citing words from the description
  - ambiguous rows get flag NEEDS_REVIEW; undecidable rows become Other + NEEDS_REVIEW
"""
import argparse
import csv

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

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogging", "knee-deep", "submerged", "inundated"],
    "Streetlight": ["streetlight", "street lights", "lights out", "light out", "lamp", "lighting", "darkness", "substation", "unlit"],
    "Waste": ["garbage", "waste", "bins", "bin", "dump", "dumped", "litter", "dead animal", "debris"],
    "Noise": ["noise", "noisy", "music", "loud", "band", "amplifier"],
    "Road Damage": ["cracked", "sinking", "subsided", "subsidence", "buckled", "footpath", "manhole", "pavement", "paving", "cobblestone", "road surface"],
    "Heritage Damage": [],
    "Heat Hazard": ["heatwave", "heat wave", "high temperature", "heat", "temperature", "melting", "°c", "sun"],
    "Drain Blockage": ["drain", "drainage", "clogged", "blocked"],
}

# Heritage Damage is only a real category when a heritage asset is actually damaged,
# not when "heritage" is used merely to describe an area.
HERITAGE_WORDS = ["heritage", "historic", "historical", "ancient", "monument"]
HERITAGE_DAMAGE_WORDS = ["defaced", "removed", "not replaced", "damage", "knocked", "subsidence", "broken", "paving"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse",
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _find_matches(text: str, mapping: dict) -> list:
    lowered = text.lower()
    matches = []
    for category, keywords in mapping.items():
        for keyword in keywords:
            if keyword in lowered:
                matches.append((category, keyword))
    has_heritage_word = any(w in lowered for w in HERITAGE_WORDS)
    has_heritage_damage = any(w in lowered for w in HERITAGE_DAMAGE_WORDS)
    if has_heritage_word and has_heritage_damage:
        matches.append(("Heritage Damage", "heritage + damage context"))
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id") or row.get("id") or ""
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    matches = _find_matches(description, CATEGORY_KEYWORDS)
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in description.lower()]
    matched_categories = {category for category, _ in matches}

    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence = "no category keyword found"
    else:
        by_category = {}
        for cat, kw in matches:
            by_category.setdefault(cat, []).append(kw)
        top_count = max(len(kws) for kws in by_category.values())
        best = [cat for cat, kws in by_category.items() if len(kws) == top_count]
        category = best[0]
        evidence = ", ".join(by_category[category])
        flag = "NEEDS_REVIEW" if len(best) > 1 else ""

    if severity_hits:
        priority = "Urgent"
        reason = f"Description mentions '{severity_hits[0]}'; matched category '{category}' via: {evidence}"
    elif category == "Noise":
        priority = "Low"
        reason = f"Routine {category} complaint with no urgency keywords; matched via: {evidence}"
    else:
        priority = "Standard"
        reason = f"Matched category '{category}' via: {evidence}"

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id") or row.get("id") or "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row could not be classified.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
