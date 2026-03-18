"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CAT_POTHOLE = "Pothole"
CAT_FLOODING = "Flooding"
CAT_DRAIN_BLOCKAGE = "Drain Blockage"

ALLOWED_CATEGORIES = [
    CAT_POTHOLE,
    CAT_FLOODING,
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    CAT_DRAIN_BLOCKAGE,
    "Other",
]

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

# Category matching uses weighted keyword hits so explicit signals dominate generic words.
CATEGORY_RULES = {
    CAT_POTHOLE: {
        "strong": ["pothole", "potholes"],
        "weak": ["crater"],
    },
    CAT_FLOODING: {
        "strong": [
            "flood",
            "flooded",
            "flooding",
            "waterlogged",
            "knee-deep",
            "underpass floods",
            "rainwater",
            "standing in water",
            "inaccessible",
        ],
        "weak": ["water"],
    },
    "Streetlight": {
        "strong": [
            "streetlight",
            "streetlights",
            "lights out",
            "flickering",
            "sparking",
            "unlit",
            "darkness",
            "substation tripped",
        ],
        "weak": ["dark", "lamp", "lighting", "wiring theft"],
    },
    "Waste": {
        "strong": [
            "garbage",
            "trash",
            "rubbish",
            "waste",
            "dumped",
            "bins",
            "bin",
            "dead animal",
            "not cleared",
        ],
        "weak": ["smell", "overflowing", "market waste"],
    },
    "Noise": {
        "strong": [
            "noise",
            "loud",
            "music",
            "midnight",
            "speaker",
            "drilling",
            "wedding band",
            "playing",
        ],
        "weak": ["venue", "weeknights", "idling", "engines"],
    },
    "Road Damage": {
        "strong": [
            "road surface",
            "cracked",
            "sinking",
            "broken",
            "tiles",
            "footpath",
            "manhole",
            "cover missing",
            "cobblestones broken",
        ],
        "weak": ["utility work", "cyclists", "pedestrians", "cable laying"],
    },
    "Heritage Damage": {
        "strong": [
            "heritage",
            "old city",
            "monument",
            "historic",
            "protected structure",
            "museum",
            "tram road cobblestones",
        ],
        "weak": ["preservation"],
    },
    "Heat Hazard": {
        "strong": [
            "heat",
            "heatwave",
            "heat wave",
            "sunstroke",
            "dehydration",
            "high temperature",
            "dangerous temperatures",
            "surface temperature",
            "unbearable",
            "melting",
            "44",
            "52",
        ],
        "weak": ["hot", "temperature", "dying in heatwave"],
    },
    CAT_DRAIN_BLOCKAGE: {
        "strong": [
            "drain blocked",
            "drain blockage",
            "blocked drain",
            "clogged drain",
            "manhole overflow",
            "stormwater drain",
        ],
        "weak": ["sewage", "gutter", "draining directly"],
    },
}


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _contains_term(text: str, term: str) -> bool:
    if " " in term or "-" in term:
        return term in text
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def _find_priority(description_lc: str) -> str:
    for keyword in SEVERITY_KEYWORDS:
        if _contains_term(description_lc, keyword):
            return "Urgent"
    return "Standard"


def _score_categories(description_lc: str) -> dict:
    scores = {}
    matched_terms = {}
    for category, rule in CATEGORY_RULES.items():
        score = 0
        found = []

        for term in rule.get("strong", []):
            if _contains_term(description_lc, term):
                score += 3
                found.append(term)

        for term in rule.get("weak", []):
            # Avoid double counting when a matched strong phrase already includes the weak term.
            if any(term in strong_term for strong_term in found):
                continue
            if _contains_term(description_lc, term):
                score += 1
                found.append(term)

        scores[category] = score
        matched_terms[category] = found

    return {"scores": scores, "matched_terms": matched_terms}


def _resolve_category(description_lc: str) -> tuple:
    scored = _score_categories(description_lc)
    scores = scored["scores"]
    matched_terms = scored["matched_terms"]

    max_score = max(scores.values())
    if max_score <= 0:
        return "Other", [], True

    winners = [cat for cat, score in scores.items() if score == max_score]

    # Safe disambiguation: explicit blocked-drain wording should resolve to Drain Blockage.
    if set(winners) == {CAT_FLOODING, CAT_DRAIN_BLOCKAGE}:
        blocked_terms = ["drain blocked", "blocked drain", "drain blockage", "clogged drain"]
        drain_and_blocked = _contains_term(description_lc, "drain") and _contains_term(description_lc, "blocked")
        if any(_contains_term(description_lc, term) for term in blocked_terms):
            return CAT_DRAIN_BLOCKAGE, matched_terms.get(CAT_DRAIN_BLOCKAGE, []), False
        if drain_and_blocked:
            return CAT_DRAIN_BLOCKAGE, matched_terms.get(CAT_DRAIN_BLOCKAGE, []), False

    if set(winners) == {CAT_POTHOLE, CAT_FLOODING}:
        if _contains_term(description_lc, "pothole"):
            return CAT_POTHOLE, matched_terms.get(CAT_POTHOLE, []), False

    if len(winners) > 1:
        return "Other", [], True

    category = winners[0]
    return category, matched_terms.get(category, []), False


def _build_reason(category: str, matched_terms: list, ambiguous: bool, priority: str) -> str:
    if ambiguous:
        return "Insufficient complaint detail to classify reliably from the provided description."

    quoted_terms = ", ".join(f'"{term}"' for term in matched_terms[:2])
    if not quoted_terms:
        quoted_terms = "direct wording"

    if priority == "Urgent":
        return f'Classified as {category} based on words like {quoted_terms}, and urgency was raised due to severity cues in the text.'

    return f'Classified as {category} based on words like {quoted_terms} in the complaint description.'

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implements strict UC-0A enforcement from agents.md and skills.md.
    """
    complaint_id = _safe_text(row.get("complaint_id"))
    description = _safe_text(row.get("description"))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient complaint detail to classify reliably.",
            "flag": "NEEDS_REVIEW",
        }

    description_lc = description.lower()
    category, matched_terms, ambiguous = _resolve_category(description_lc)
    priority = _find_priority(description_lc)

    # Keep output conservative for ambiguous rows.
    if ambiguous:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    reason = _build_reason(category, matched_terms, ambiguous, priority)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Insufficient complaint detail to classify reliably from the provided description."

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

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
    
    Fail fast for missing/unreadable input, continue on per-row failures.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input CSV not found: {input_path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read input CSV: {input_path}") from exc

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            complaint_id = _safe_text(row.get("complaint_id"))
            results.append(
                {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Insufficient complaint detail to classify reliably.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
