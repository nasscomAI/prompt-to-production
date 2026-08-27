"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, Iterable, List, Tuple


ALLOWED_CATEGORIES = (
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
)

PRIORITY_URGENT = "Urgent"
PRIORITY_STANDARD = "Standard"
PRIORITY_LOW = "Low"
FLAG_REVIEW = "NEEDS_REVIEW"

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

CATEGORY_PATTERNS = {
    "Pothole": (
        "pothole",
        "potholes",
    ),
    "Flooding": (
        "flood",
        "flooded",
        "flooding",
        "standing in water",
        "knee-deep",
        "stranded",
        "underpass floods",
        "becomes inaccessible",
    ),
    "Streetlight": (
        "streetlight",
        "streetlights",
        "lights out",
        "unlit",
        "very dark",
        "darkness",
        "lamp post",
        "flickering",
        "sparking",
    ),
    "Waste": (
        "garbage",
        "waste",
        "overflowing",
        "overflow",
        "bins",
        "bin",
        "dead animal",
        "not cleared",
        "piles of waste",
    ),
    "Noise": (
        "music",
        "drilling",
        "amplifiers",
        "audible",
        "trucks idling",
        "engines on",
        "playing",
    ),
    "Road Damage": (
        "road surface",
        "cracked",
        "sinking",
        "collapsed",
        "collapse",
        "crater",
        "subsidence",
        "subsided",
        "buckled",
        "broken",
        "upturned",
        "manhole cover missing",
        "tiles broken",
    ),
    "Heritage Damage": (
        "heritage damage",
        "historic",
        "heritage",
        "cobblestones",
        "museum",
        "step well",
        "tram road",
        "defaced",
        "not restored",
        "stone not replaced",
    ),
    "Heat Hazard": (
        "heat",
        "heatwave",
        "44°c",
        "45°c",
        "52°c",
        "temperature",
        "temperatures",
        "melting",
        "full sun",
        "burns",
        "unsafe",
    ),
    "Drain Blockage": (
        "drain blocked",
        "drain completely blocked",
        "main drain blocked",
        "stormwater drain",
        "blocked with construction debris",
        "mosquito breeding",
        "drainage",
    ),
}

OUTSIDE_TAXONOMY_PATTERNS = (
    "irrigation system",
    "trees",
    "tree",
    "bench",
    "shelter roof glass",
    "substation",
)


def _find_matches(text: str, patterns: Iterable[str]) -> List[str]:
    return [pattern for pattern in patterns if pattern in text]


def _first_phrase(description: str, matches: Iterable[str]) -> str:
    lowered = description.lower()
    for match in matches:
        index = lowered.find(match)
        if index != -1:
            return description[index:index + len(match)]
    return description[:40].strip() or "description"


def _priority_from_text(text: str, days_open: str) -> Tuple[str, List[str]]:
    severity_hits = _find_matches(text, SEVERITY_KEYWORDS)
    if severity_hits:
        return PRIORITY_URGENT, severity_hits

    if days_open:
        try:
            if int(days_open) >= 21:
                return PRIORITY_LOW, []
        except ValueError:
            pass

    return PRIORITY_STANDARD, []


def _category_from_description(description: str) -> Tuple[str, List[str], str]:
    text = description.lower()

    if not text.strip():
        return "Other", [], FLAG_REVIEW

    if any(pattern in text for pattern in OUTSIDE_TAXONOMY_PATTERNS):
        return "Other", [], FLAG_REVIEW

    flood_hits = _find_matches(text, CATEGORY_PATTERNS["Flooding"])
    drain_hits = _find_matches(text, CATEGORY_PATTERNS["Drain Blockage"])
    if flood_hits:
        return "Flooding", flood_hits, ""
    if drain_hits:
        return "Drain Blockage", drain_hits, ""

    heritage_hits = _find_matches(text, CATEGORY_PATTERNS["Heritage Damage"])
    road_hits = _find_matches(text, CATEGORY_PATTERNS["Road Damage"])
    if heritage_hits and road_hits:
        heritage_damage_terms = ("defaced", "not restored", "stone not replaced", "cobblestones")
        if any(term in text for term in heritage_damage_terms):
            return "Heritage Damage", heritage_hits, ""
        return "Other", sorted(set(heritage_hits + road_hits)), FLAG_REVIEW

    ordered_categories = (
        "Pothole",
        "Streetlight",
        "Waste",
        "Noise",
        "Heat Hazard",
        "Road Damage",
        "Heritage Damage",
    )

    matches_by_category: Dict[str, List[str]] = {}
    for category in ordered_categories:
        hits = _find_matches(text, CATEGORY_PATTERNS[category])
        if hits:
            matches_by_category[category] = hits

    if len(matches_by_category) > 1:
        categories = set(matches_by_category)
        if categories == {"Streetlight", "Heritage Damage"}:
            return "Streetlight", matches_by_category["Streetlight"], ""
        if categories == {"Waste", "Heritage Damage"}:
            return "Waste", matches_by_category["Waste"], ""
        return "Other", sorted({hit for hits in matches_by_category.values() for hit in hits}), FLAG_REVIEW

    if matches_by_category:
        category = next(iter(matches_by_category))
        return category, matches_by_category[category], ""

    if "draining directly onto public road" in text or "channel rainwater" in text:
        return "Other", ["rainwater", "public road"], FLAG_REVIEW

    return "Other", [], FLAG_REVIEW

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    days_open = (row.get("days_open") or "").strip()

    category, category_hits, flag = _category_from_description(description)
    priority, severity_hits = _priority_from_text(description.lower(), days_open)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": PRIORITY_STANDARD,
            "reason": "Marked Other because the description is missing, so there are no words to classify.",
            "flag": FLAG_REVIEW,
        }

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = FLAG_REVIEW

    reason_fragments: List[str] = []
    if category_hits:
        quoted = ", ".join(f'"{_first_phrase(description, [match])}"' for match in category_hits[:2])
        reason_fragments.append(f'assigned {category} because the description says {quoted}')
    else:
        reason_fragments.append("assigned Other because the description does not map cleanly to the approved categories")

    if severity_hits:
        quoted = ", ".join(f'"{_first_phrase(description, [match])}"' for match in severity_hits[:2])
        reason_fragments.append(f'priority is Urgent because it includes severity words {quoted}')
    elif priority == PRIORITY_LOW:
        reason_fragments.append(f'priority is Low because the complaint has been open for {days_open} days without an urgent trigger')
    else:
        reason_fragments.append("priority is Standard because no urgent severity keyword is present")

    if flag == FLAG_REVIEW:
        reason_fragments.append("flagged NEEDS_REVIEW because the issue is ambiguous or outside the taxonomy")

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": "; ".join(reason_fragments) + ".",
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as input_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # pragma: no cover - defensive row fallback
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": PRIORITY_STANDARD,
                    "reason": f'Marked Other because row processing failed with "{exc}".',
                    "flag": FLAG_REVIEW,
                }

            writer.writerow({key: result.get(key, "") for key in fieldnames})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
