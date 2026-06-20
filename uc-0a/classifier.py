"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path


ALLOWED_CATEGORIES = [
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


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _first_match(text: str, phrases: list[str]) -> str | None:
    for phrase in phrases:
        if phrase in text:
            return phrase
    return None


def _priority_for(description_lower: str) -> str:
    return "Urgent" if _contains_any(description_lower, URGENT_KEYWORDS) else "Standard"


def _build_reason(category: str, evidence: str, priority: str, review: bool, urgent_word: str | None = None) -> str:
    reason = f'Classified as {category} because the description says "{evidence}"'
    if priority == "Urgent":
        if urgent_word is None:
            urgent_word = "severity keyword"
        reason += f' and includes urgent signal "{urgent_word}"'
    if review:
        reason += " and the wording remains ambiguous"
    return reason + "."


def _detect_category(description: str) -> tuple[str, str, str]:
    text = description.lower().strip()

    heritage_terms = ["heritage", "historic", "old city", "museum", "step well", "lamp post", "cobblestones"]
    heritage_damage_terms = ["knocked over", "broken up", "defaced", "not restored", "not replaced"]
    heat_terms = [
        "heatwave",
        "44°",
        "45°",
        "52°",
        "temperature",
        "temperatures",
        "full sun",
        "burns on contact",
        "surface melting",
        "storing heat",
        "unbearable",
        "dangerous temperatures",
    ]
    pothole_terms = ["pothole", "potholes"]
    flooding_terms = ["flooded", "floods", "flooding", "standing in water", "rainwater through main road"]
    drain_terms = ["drain blocked", "drain completely blocked", "main drain blocked", "stormwater drain", "mosquito breeding"]
    streetlight_terms = ["streetlight", "streetlights", "lights out", "unlit", "darkness", "flickering", "sparking"]
    waste_terms = ["garbage", "waste", "overflowing", "bins", "dumped", "dead animal", "not removed", "not cleared"]
    noise_terms = ["music", "drilling", "amplifiers", "trucks idling", "engines on", "band playing"]
    road_damage_terms = [
        "road surface",
        "cracked",
        "sinking",
        "subsidence",
        "subsided",
        "collapsed",
        "buckled",
        "broken and upturned",
        "broken",
        "upturned",
        "manhole cover missing",
        "tiles broken",
        "footpath broken",
        "surface bubbling",
        "missing",
        "crater",
    ]

    if _contains_any(text, heritage_terms) and _contains_any(text, heritage_damage_terms):
        evidence = _first_match(text, heritage_damage_terms) or "heritage"
        return "Heritage Damage", evidence, ""

    if _contains_any(text, heat_terms):
        evidence = _first_match(text, heat_terms) or "heatwave"
        return "Heat Hazard", evidence, ""

    if _contains_any(text, pothole_terms):
        evidence = _first_match(text, pothole_terms) or "pothole"
        return "Pothole", evidence, ""

    has_flooding = _contains_any(text, flooding_terms)
    has_drain = _contains_any(text, drain_terms)
    if has_flooding and not has_drain:
        evidence = _first_match(text, flooding_terms) or "flooded"
        return "Flooding", evidence, ""
    if has_drain and not has_flooding:
        evidence = _first_match(text, drain_terms) or "drain blocked"
        return "Drain Blockage", evidence, ""
    if has_flooding and has_drain:
        if text.index(_first_match(text, flooding_terms) or "flooded") <= text.index(_first_match(text, drain_terms) or "drain blocked"):
            evidence = _first_match(text, flooding_terms) or "flooded"
            return "Flooding", evidence, "NEEDS_REVIEW"
        evidence = _first_match(text, drain_terms) or "drain blocked"
        return "Drain Blockage", evidence, "NEEDS_REVIEW"

    if _contains_any(text, streetlight_terms):
        evidence = _first_match(text, streetlight_terms) or "streetlight"
        return "Streetlight", evidence, ""

    if _contains_any(text, waste_terms):
        evidence = _first_match(text, waste_terms) or "waste"
        return "Waste", evidence, ""

    if _contains_any(text, noise_terms):
        evidence = _first_match(text, noise_terms) or "noise"
        return "Noise", evidence, ""

    if _contains_any(text, heritage_terms) and _contains_any(text, ["road", "building", "stone", "paving", "exterior"]):
        evidence = _first_match(text, heritage_terms) or "heritage"
        return "Heritage Damage", evidence, ""

    if _contains_any(text, road_damage_terms):
        evidence = _first_match(text, road_damage_terms) or "road surface"
        review_flag = "NEEDS_REVIEW" if _contains_any(text, ["bench", "shelter", "substation", "trees"]) else ""
        return "Road Damage", evidence, review_flag

    if _contains_any(text, ["trees", "bench", "shelter", "substation", "park users unsafe"]):
        evidence = _first_match(text, ["trees", "bench", "shelter", "substation", "park users unsafe"]) or "unsafe"
        return "Other", evidence, "NEEDS_REVIEW"

    return "Other", description.strip()[:80], "NEEDS_REVIEW"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        evidence = "missing description"
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": _build_reason("Other", evidence, "Low", True),
            "flag": "NEEDS_REVIEW",
        }

    category, evidence, preset_flag = _detect_category(description)
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        preset_flag = "NEEDS_REVIEW"
        evidence = description[:80]

    priority = _priority_for(description.lower())
    urgent_word = _first_match(description.lower(), URGENT_KEYWORDS)
    if category == "Other" and priority == "Standard":
        priority = "Low"

    flag = preset_flag
    reason = _build_reason(category, evidence, priority, bool(flag), urgent_word)
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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", newline="", encoding="utf-8") as infile, output_file.open(
        "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                writer.writerow(classify_complaint(row))
            except Exception as exc:
                complaint_id = (row.get("complaint_id") or "").strip()
                fallback_reason = f'Classified as Other because processing failed with "{str(exc)}" and the row needs review.'
                writer.writerow(
                    {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": fallback_reason,
                        "flag": "NEEDS_REVIEW",
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
