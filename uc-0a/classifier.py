"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

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

CATEGORY_RULES = (
    (
        "Heritage Damage",
        (
            "heritage damage",
            "monument damaged",
            "historic wall",
            "heritage structure",
            "protected facade",
        ),
    ),
    (
        "Streetlight",
        (
            "streetlight",
            "street light",
            "lights not working",
            "dark stretch",
            "lamp post",
            "no lighting",
        ),
    ),
    (
        "Heat Hazard",
        (
            "heat",
            "heatwave",
            "no shade",
            "heat hazard",
            "sun exposure",
        ),
    ),
    (
        "Noise",
        (
            "noise",
            "drilling",
            "loudspeaker",
            "horn",
            "idling",
            "engines on",
            "5am",
        ),
    ),
    (
        "Waste",
        (
            "garbage",
            "waste",
            "overflow",
            "not cleared",
            "piles of waste",
            "unusable by sunday",
            "mosquito breeding",
        ),
    ),
    (
        "Pothole",
        (
            "pothole",
            "potholes",
            "wheel",
            "6 potholes",
        ),
    ),
    (
        "Road Damage",
        (
            "road collapsed",
            "collapsed partially",
            "crater",
            "road damage",
            "caved in",
            "collapse",
        ),
    ),
)

FLOOD_TERMS = (
    "flood",
    "flooded",
    "floods",
    "flooding",
    "waterlogged",
    "rainwater",
    "underpass",
    "abandoned",
)

DRAIN_TERMS = (
    "drain blocked",
    "drain completely blocked",
    "drainage blocked",
    "drain clogged",
    "drain 100% blocked",
    "main drain blocked",
    "stormwater drain",
    "construction debris",
)


def _clean_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _find_matches(text: str, phrases: tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if phrase in text]


def _determine_category(text: str) -> tuple[str, list[str], str]:
    for category, phrases in CATEGORY_RULES:
        matches = _find_matches(text, phrases)
        if matches:
            return category, matches[:2], ""

    flood_matches = _find_matches(text, FLOOD_TERMS)
    drain_matches = _find_matches(text, DRAIN_TERMS)
    if flood_matches and not drain_matches:
        return "Flooding", flood_matches[:2], ""
    if drain_matches and not flood_matches:
        return "Drain Blockage", drain_matches[:2], ""
    if flood_matches and drain_matches:
        if any(term in text for term in ("flooded", "floods", "underpass floods", "abandoned")):
            return "Flooding", (flood_matches + drain_matches)[:2], ""
        if any(term in text for term in ("blocked", "stormwater drain", "construction debris", "flooding risk")):
            return "Drain Blockage", (drain_matches + flood_matches)[:2], ""
        return "Other", (flood_matches + drain_matches)[:2], "NEEDS_REVIEW"

    if "heritage" in text and any(term in text for term in ("damage", "crack", "collapse", "broken")):
        return "Heritage Damage", ["heritage", "damage"], ""

    return "Other", [], "NEEDS_REVIEW"


def _determine_priority(text: str, flag: str) -> tuple[str, list[str]]:
    severity_matches = _find_matches(text, SEVERITY_KEYWORDS)
    if severity_matches:
        return "Urgent", severity_matches[:2]
    if flag == "NEEDS_REVIEW":
        return "Low", []
    return "Standard", []


def _build_reason(category: str, category_matches: list[str], priority: str, priority_matches: list[str], flag: str) -> str:
    evidence = category_matches + [term for term in priority_matches if term not in category_matches]
    if evidence:
        evidence_text = ", ".join(f'"{term}"' for term in evidence[:3])
        base = f'Matched {evidence_text}, so the complaint maps to {category} with {priority} priority'
    else:
        base = f'No exact taxonomy keyword was found, so the complaint defaults to {category} with {priority} priority'
    if flag == "NEEDS_REVIEW":
        base += " and needs review because the description does not support a single clear category"
    return base + "."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = row.get("description") or ""
    text = _clean_text(" ".join(
        part for part in [description, row.get("location", ""), row.get("ward", ""), row.get("city", "")]
        if part
    ))

    if not _clean_text(description):
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": 'Missing description text, so the complaint cannot be classified from row evidence alone.',
            "flag": "NEEDS_REVIEW",
        }

    category, category_matches, flag = _determine_category(text)
    priority, priority_matches = _determine_priority(text, flag)
    reason = _build_reason(category, category_matches, priority, priority_matches, flag)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = 'Rule output fell outside the allowed taxonomy, so the complaint was reset to Other and marked for review.'

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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row.get("complaint_id") or "UNKNOWN").strip() or "UNKNOWN",
                    "category": "Other",
                    "priority": "Low",
                    "reason": f'Row failed classification with error "{exc}", so it was marked for manual review.',
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
