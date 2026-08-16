"""
UC-0A — Complaint Classifier

Deterministic keyword classification guided by agents.md + skills.md.
Reflects these RICE enforcement rules:
  - category in the exact allowed taxonomy, no variations
  - Urgent iff a severity keyword is present, else Standard
  - reason cites specific words from the description
  - NEEDS_REVIEW flag set when the category is genuinely ambiguous
  - batch never crashes on a bad row; output produced even if some rows fail
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "hospitalised", "ambulance", "fire", "hazard", "fell", "collapse",
    "collapsed", "serious injury",
]

TEMPERATURE_RE = re.compile(r"\d+\s*(°|deg|degree)\s*c\b", re.IGNORECASE)

CATEGORY_KEYWORDS = {
    "Pothole": {
        "pothole": 3, "potholes": 3, "crater": 2,
    },
    "Flooding": {
        "flooded": 3, "floods": 3, "flooding": 3, "flood": 2,
        "waterlogging": 3, "water logging": 3, "submerged": 3,
        "standing in water": 3, "inundated": 3, "rainwater": 2,
        "draining": 2, "drain onto": 2, "channel rainwater": 3,
        "channels rainwater": 3,
    },
    "Streetlight": {
        "streetlight": 3, "street light": 3, "street lights": 3,
        "lights out": 3, "lamp post": 3, "lamp posts": 3, "unlit": 3,
        "wiring": 2, "substation": 2, "sparking": 2, "lamp": 2,
        "lighting": 1, "light": 1, "dark": 1,
    },
    "Waste": {
        "garbage": 3, "litter": 3, "dead animal": 3, "dumping": 3,
        "dumped": 3, "overflowing": 3, "overflow": 2, "bins": 2,
        "not cleared": 2, "waste": 2,
    },
    "Noise": {
        "music": 3, "musical": 3, "audible": 3, "amplifier": 3,
        "amplifiers": 3, "loud": 3, "drilling": 3, "idling": 2,
        "horn": 2, "noise": 2, "vibrations": 2, "band": 2, "playing": 1,
    },
    "Road Damage": {
        "road collapsed": 3, "collapsed": 3, "road subsidence": 3,
        "subsidence": 2, "subsided": 3, "buckled": 3, "buckling": 2,
        "cracked": 2, "sinking": 2, "tarmac": 2, "footpath": 3,
        "paving": 2, "pavement": 2, "upturned paving": 3, "upturned": 1,
        "road surface": 2, "road": 1, "surface": 1,
    },
    "Heritage Damage": {
        "heritage lamp post": 3, "heritage lamp": 3, "heritage stone": 3,
        "cobblestones": 3, "cobblestone": 3, "historic tram road": 3,
        "heritage building": 3, "heritage residential": 3, "step well": 2,
        "heritage": 1, "historic": 2, "ancient": 1, "monument": 2,
    },
    "Heat Hazard": {
        "storing heat": 3, "heatwave": 3, "melting": 3, "unbearable": 2,
        "temperature": 2, "temperatures": 2, "bubbling": 2, "heat": 2,
        "sun": 1,
    },
    "Drain Blockage": {
        "drain completely blocked": 3, "drain blocked": 3,
        "blocked main drain": 3, "stormwater drain": 3, "main drain": 3,
        "debris": 2, "sewage": 3, "mosquito": 2, "gutter": 3, "manhole": 2,
        "clogged": 2, "drainage": 1, "drain": 1,
    },
}

HERITAGE_DIRECT_PHRASES = [
    "heritage lamp post", "heritage lamp", "heritage stone", "cobblestones",
    "cobblestone", "historic tram road", "heritage building",
    "heritage residential",
]


def _score_categories(text: str):
    """Return {category: (score, [matched_phrases])} for every category."""
    t = text.lower()
    results = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        matched = []
        for phrase, weight in keywords.items():
            if phrase in t:
                score += weight
                matched.append(phrase)
        if category == "Heat Hazard" and TEMPERATURE_RE.search(text):
            score += 3
            matched.append(TEMPERATURE_RE.search(text).group(0))
        results[category] = (score, matched)
    return results


def resolve_category(description: str):
    """Return (category, needs_review) for a non-empty description."""
    t = description.lower()
    scores = _score_categories(description)
    top = max(scores, key=lambda c: (scores[c][0], -ALLOWED_CATEGORIES.index(c)))
    top_score = scores[top][0]

    # Heritage direct damage overrides other signals (the heritage element is
    # itself damaged).
    for phrase in HERITAGE_DIRECT_PHRASES:
        if phrase in t:
            flag = "NEEDS_REVIEW" if ("lamp" in t or "light" in t) else ""
            return "Heritage Damage", flag

    # No meaningful match -> cannot fit taxonomy.
    if top_score < 2:
        return "Other", "NEEDS_REVIEW"

    if top == "Other":
        return "Other", "NEEDS_REVIEW"

    # Flooding + blocked-drain co-occurrence: both categories genuinely apply.
    has_flood = any(p in t for p in ("flooded", "floods", "flooding", "flood",
                                     "waterlogging", "standing in water"))
    has_blocked_drain = any(p in t for p in ("drain blocked", "drain completely "
                                             "blocked", "blocked main drain",
                                             "stormwater drain", "clogged"))
    if has_flood and has_blocked_drain:
        return top, "NEEDS_REVIEW"

    # Manhole (drainage infrastructure) but with a safety hazard that is not a
    # blockage: drainage category with an ambiguity flag.
    if "manhole" in t:
        return "Drain Blockage", "NEEDS_REVIEW"

    # Heat-caused road surface damage: both Heat Hazard and Road Damage apply.
    if "bubbling" in t and t:
        heat = scores["Heat Hazard"][0]
        road = scores["Road Damage"][0]
        if abs(heat - road) <= 1:
            return top, "NEEDS_REVIEW"

    # Heritage mentioned as context (not directly damaged), and the top
    # category is one that could plausibly be heritage-related.
    if "heritage" in t or "historic" in t or "ancient" in t:
        if top in ("Streetlight", "Road Damage"):
            return top, "NEEDS_REVIEW"

    return top, ""


def _fallback_tokens(description: str, limit: int = 4):
    words = [w.strip(" ,.") for w in description.split() if len(w) > 3]
    return ", ".join(words[:limit])


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = str(row.get("complaint_id") or "").strip() or "UNKNOWN"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = resolve_category(description)

    severity = [k for k in SEVERITY_KEYWORDS if k in description.lower()]
    priority = "Urgent" if severity else "Standard"

    matched = _score_categories(description).get(category, (0, []))[1]
    if matched:
        evidence = ", ".join(matched[:6])
        reason = f"Classification is based on description mention of: {evidence}."
    else:
        reason = f"No allowed category matched; evidence in description: {_fallback_tokens(description)}."
    if severity:
        reason += f" Severity keywords present: {', '.join(severity[:4])}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, newline="", encoding="utf-8") as inf, \
         open(output_path, "w", newline="", encoding="utf-8") as outf:
        reader = csv.DictReader(inf)
        writer = csv.DictWriter(outf, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never crash the batch on a bad row
                result = {
                    "complaint_id": str(row.get("complaint_id") or "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing failed: {exc}.",
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