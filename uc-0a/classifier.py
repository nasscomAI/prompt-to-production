"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from pathlib import Path

ALLOWED_CATEGORIES = {
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
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

MANDATORY_URGENT_KEYWORDS = (
    "injury",
    "child",
    "children",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
)

CATEGORY_RULES = (
    (
        "Heritage Damage",
        (
            "heritage lamp post",
            "heritage residential building",
            "heritage stone",
            "step well",
            "ancient step well",
            "historic tram road cobblestones",
            "cobblestones broken",
            "knocked over",
            "defaced",
            "not restored",
            "billboard installation",
            "old city road subsidence",
            "road subsidence near ancient step well",
            "heritage concern",
        ),
    ),
    (
        "Streetlight",
        (
            "streetlight",
            "streetlights",
            "lights out",
            "lamp post",
            "darkness",
            "very dark",
            "flickering",
            "sparking",
            "substation tripped",
            "dark at night",
            "unlit",
            "wiring theft",
            "darkness for",
        ),
    ),
    (
        "Heat Hazard",
        (
            "heatwave",
            "dangerous temperatures",
            "surface temperature",
            "52°c",
            "unbearable",
            "burns",
            "storing heat",
            "hot metal",
            "melting",
            "44°c",
            "45°c",
            "surface bubbling",
        ),
    ),
    (
        "Noise",
        (
            "drilling",
            "5am",
            "amplifiers",
            "wedding band",
            "delivery trucks idling",
            "engines on",
            "noise",
            "loud",
            "music past midnight",
            "club music",
            "audible at residential buildings",
        ),
    ),
    (
        "Waste",
        (
            "garbage",
            "waste",
            "overflowing bins",
            "overflow",
            "bins overflowing",
            "piles of waste",
            "not cleared",
            "dumped on public road",
            "post-market waste",
            "dead animal",
        ),
    ),
    (
        "Pothole",
        (
            "pothole",
            "potholes",
            "tyre damage",
            "tyre blowouts",
            "motorcycle wheel",
        ),
    ),
    (
        "Road Damage",
        (
            "road collapsed",
            "collapsed partially",
            "crater",
            "subsidence",
            "road damage",
            "paving removed",
            "lane closure",
            "bridge approach",
            "cracked and sinking",
            "sinking",
            "manhole cover missing",
            "footpath broken",
            "footpath tiles broken",
            "tiles broken",
            "buckled",
            "road subsided",
            "gas leak",
        ),
    ),
    (
        "Flooding",
        (
            "flooded",
            "floods",
            "flooding",
            "underpass",
            "standing in water",
            "stranded",
            "abandoned",
            "rainwater through main road",
            "knee-deep",
            "draining directly onto public road",
        ),
    ),
    (
        "Drain Blockage",
        (
            "drain blocked",
            "drain completely blocked",
            "main drain blocked",
            "stormwater drain",
            "100% blocked",
            "construction debris",
            "mosquito breeding",
        ),
    ),
)


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _collect_evidence(description: str, location: str) -> list[str]:
    evidence = []
    description_lower = description.lower()
    location_lower = location.lower()
    for needle in (
        "ambulance",
        "school",
        "hospital",
        "hazard",
        "collapse",
        "collapsed",
        "flooded",
        "floods",
        "drain blocked",
        "stormwater drain",
        "pothole",
        "unlit",
        "garbage",
        "waste",
        "streetlight",
        "lights out",
        "drilling",
        "music",
        "heatwave",
        "melting",
        "heritage",
        "crater",
        "manhole cover missing",
        "footpath broken",
        "gas leak",
    ):
        if needle in description_lower or needle in location_lower:
            evidence.append(needle)

    if not evidence:
        fallback_words = description.split()[:6]
        return [" ".join(fallback_words)] if fallback_words else ["missing description"]

    return evidence[:3]


def _priority_for_text(description: str) -> str:
    description_lower = description.lower()
    if any(keyword in description_lower for keyword in MANDATORY_URGENT_KEYWORDS):
        return "Urgent"

    high_risk_signals = (
        "risk",
        "electrical",
        "sparking",
        "stranded",
        "abandoned",
        "accident",
        "dark at night",
        "dengue",
        "mosquito breeding",
        "unsafe",
        "gas leak",
        "health concern",
        "injured",
        "elderly",
    )
    if any(signal in description_lower for signal in high_risk_signals):
        return "Urgent"

    low_signals = (
        "delivery trucks idling",
        "engines on",
    )
    if any(signal in description_lower for signal in low_signals):
        return "Low"

    return "Standard"


def _match_category(description: str, location: str) -> tuple[str, str]:
    haystack = f"{description} {location}".lower()
    matches = []

    for category, keywords in CATEGORY_RULES:
        matched = [keyword for keyword in keywords if keyword in haystack]
        if matched:
            matches.append((category, matched))

    if not matches:
        return "Other", "NEEDS_REVIEW"

    if len(matches) == 1:
        return matches[0][0], ""

    categories = {category for category, _ in matches}

    if "Drain Blockage" in categories and "Flooding" in categories:
        drain_match = next(matched for category, matched in matches if category == "Drain Blockage")
        direct_flooding = any(
            token in haystack for token in ("flooded", "floods", "knee-deep", "standing in water", "stranded")
        )
        future_risk_only = "flooding risk" in haystack and not direct_flooding
        if future_risk_only:
            return "Drain Blockage", ""
        if direct_flooding:
            return "Flooding", ""
        if any("blocked" in keyword or "drain" in keyword for keyword in drain_match):
            return "Drain Blockage", ""
        return "Flooding", ""

    if "Waste" in categories and "Heritage Damage" in categories:
        return "Waste", ""

    if "Streetlight" in categories and "Heritage Damage" in categories:
        if any(token in haystack for token in ("knocked over", "not restored", "defaced", "heritage stone")):
            return "Heritage Damage", ""
        return "Streetlight", ""

    if "Heritage Damage" in categories and "Road Damage" in categories:
        if "heritage" in haystack or "step well" in haystack or "cobblestones" in haystack:
            return "Heritage Damage", ""
        return "Road Damage", ""

    if "Road Damage" in categories and "Pothole" in categories:
        if "crater" in haystack or "collapsed" in haystack or "subsidence" in haystack:
            return "Road Damage", ""
        return "Pothole", ""

    if "Flooding" in categories and "Road Damage" in categories:
        return "Flooding", ""

    return "Other", "NEEDS_REVIEW"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    """
    complaint_id = _clean_text(row.get("complaint_id")) or "UNKNOWN"
    description = _clean_text(row.get("description"))
    location = _clean_text(row.get("location"))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Marked Other because the description is missing, so the category cannot be determined from the row.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = _match_category(description, location)
    priority = _priority_for_text(description)
    evidence = ", ".join(f'"{item}"' for item in _collect_evidence(description, location))
    reason = f"Classified as {category} because the row cites {evidence}; priority is {priority} based on the same complaint text."

    result = {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

    if result["category"] not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    if result["priority"] not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"
        result["flag"] = "NEEDS_REVIEW"

    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, newline="", encoding="utf-8") as input_handle, open(
        output_file, "w", newline="", encoding="utf-8"
    ) as output_handle:
        reader = csv.DictReader(input_handle)
        writer = csv.DictWriter(output_handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for row in reader:
            safe_row = row or {}
            try:
                result = classify_complaint(safe_row)
            except Exception as exc:
                complaint_id = _clean_text(safe_row.get("complaint_id")) or "UNKNOWN"
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Marked Other because this row could not be classified safely: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow({field: result.get(field, "") for field in OUTPUT_FIELDS})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
