"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple


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

REVIEW_REQUIRED = "NEEDS_REVIEW"
REVIEW_NOT_REQUIRED = "not required"

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
]

LOW_PRIORITY_HINTS = [
    "noise",
    "music",
    "midnight",
    "smell",
    "idling",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "road pit"],
    "Flooding": ["flood", "flooded", "waterlogged", "water logging", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "sparking", "dark at night", "darkness", "unlit"],
    "Waste": ["garbage", "trash", "waste", "dumped", "dead animal", "overflowing bins"],
    "Noise": ["noise", "loudspeaker", "music", "past midnight", "weeknights", "wedding venue", "wedding band", "amplifier", "amplifiers", "drilling", "5am", "2am", "idling"],
    "Road Damage": ["cracked", "sinking", "road surface", "footpath tiles", "manhole cover missing", "road collapsed", "buckled", "subsided", "upturned paving", "crater"],
    "Heritage Damage": [],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "extreme heat", "melting", "burns", "unbearable", "full sun", "dangerous temperatures", "45c", "52c"],
    "Drain Blockage": ["drain blocked", "blocked drain", "clogged drain", "drain choke", "manhole blocked"],
}

HERITAGE_CONTEXT = [
    "heritage",
    "historic",
    "monument",
    "museum",
    "old city",
    "precinct",
    "tram road",
    "lamp post",
    "stone",
]

HERITAGE_DAMAGE_MARKERS = [
    "damaged",
    "defaced",
    "broken",
    "collapsed",
    "removed",
    "not restored",
    "not replaced",
    "knocked over",
]


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _score_categories(description_lc: str) -> Dict[str, int]:
    scores = {category: 0 for category in ALLOWED_CATEGORIES if category != "Other"}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description_lc:
                scores[category] += 1
    return scores


def _contains_word(description_lc: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", description_lc) is not None


def _is_heritage_damage(description_lc: str) -> bool:
    has_context = any(term in description_lc for term in HERITAGE_CONTEXT)
    has_damage = any(term in description_lc for term in HERITAGE_DAMAGE_MARKERS)
    return has_context and has_damage


def _is_drain_blockage(description_lc: str) -> bool:
    if any(term in description_lc for term in CATEGORY_KEYWORDS["Drain Blockage"]):
        return True
    # Capture phrasing like "drain 100% blocked" or "main drain ... blocked".
    return re.search(r"\bdrain\b.{0,30}\bblocked\b", description_lc) is not None


def _is_clear_road_damage(description_lc: str) -> bool:
    # Deterministic road-failure phrasing that should not be marked ambiguous.
    if "road collapsed" in description_lc:
        return True
    if "upturned paving" in description_lc:
        return True
    return False


def _pick_category(scores: Dict[str, int]) -> Tuple[str, bool, List[str]]:
    non_zero = {k: v for k, v in scores.items() if v > 0}
    if not non_zero:
        return "Other", True, []

    ranked = sorted(non_zero.items(), key=lambda item: item[1], reverse=True)
    top_score = ranked[0][1]
    top_categories = sorted([k for k, v in ranked if v == top_score])

    # If multiple categories tie with equal evidence, treat as ambiguous.
    if len(top_categories) > 1:
        return "Other", True, top_categories

    # If multiple categories are triggered and confidence margin is weak, review instead of guessing.
    if len(ranked) > 1:
        second_score = ranked[1][1]
        if top_score - second_score <= 1:
            candidates = sorted([ranked[0][0], ranked[1][0]])
            return "Other", True, candidates

    # If too many categories are triggered in one complaint, treat as mixed signal.
    if len(non_zero) >= 3:
        candidates = sorted(non_zero.keys())
        return "Other", True, candidates

    return top_categories[0], False, [top_categories[0]]


def _determine_priority(description_lc: str) -> str:
    if any(_contains_word(description_lc, keyword) for keyword in SEVERITY_KEYWORDS):
        return "Urgent"
    if any(keyword in description_lc for keyword in LOW_PRIORITY_HINTS):
        return "Low"
    return "Standard"


def _build_reason(category: str, priority: str, description: str, evidence_terms: List[str]) -> str:
    evidence_word = ""
    description_lc = description.lower()

    for term in SEVERITY_KEYWORDS:
        if term in description_lc:
            evidence_word = term
            break

    if not evidence_word:
        for term in evidence_terms:
            if term in description_lc:
                evidence_word = term
                break

    if not evidence_word and description.strip():
        evidence_word = description.strip().split()[0].strip(",.?!:;\"'()[]{}")

    if not evidence_word:
        return "Insufficient description to determine issue type."

    return f"Marked as {category} with {priority} priority because the description includes '{evidence_word}'."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Rules enforced:
    - category from allowed taxonomy only
    - priority uses urgency keywords
    - reason is one sentence with evidence from text
    - ambiguous/unreadable rows are flagged NEEDS_REVIEW
    """
    complaint_id = _safe_text(row.get("complaint_id"))
    description = _safe_text(row.get("description"))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient description to determine issue type.",
            "flag": REVIEW_REQUIRED,
        }

    description_lc = description.lower()

    # Deterministic overrides for patterns that should not be guessed from generic scoring.
    if _is_heritage_damage(description_lc):
        category, ambiguous, top_categories = "Heritage Damage", False, ["Heritage Damage"]
    elif _is_drain_blockage(description_lc):
        category, ambiguous, top_categories = "Drain Blockage", False, ["Drain Blockage"]
    elif _is_clear_road_damage(description_lc):
        category, ambiguous, top_categories = "Road Damage", False, ["Road Damage"]
    else:
        scores = _score_categories(description_lc)
        category, ambiguous, top_categories = _pick_category(scores)

    priority = _determine_priority(description_lc)
    flag = REVIEW_REQUIRED if ambiguous else REVIEW_NOT_REQUIRED

    # If ambiguous but severity is obvious, keep Urgent while retaining review flag.
    reason_source_terms: List[str] = []
    if category in CATEGORY_KEYWORDS:
        reason_source_terms.extend(CATEGORY_KEYWORDS[category])
    for candidate in top_categories:
        reason_source_terms.extend(CATEGORY_KEYWORDS.get(candidate, []))

    reason = _build_reason(category, priority, description, reason_source_terms)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = REVIEW_REQUIRED

    if priority not in {"Urgent", "Standard", "Low"}:
        priority = "Standard"
        flag = REVIEW_REQUIRED

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
    
    Reads input CSV and writes output CSV with classification fields.
    Continues per-row even if one row is malformed.
    """
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no headers.")

        output_fields = list(reader.fieldnames)
        for field in ["category", "priority", "reason", "flag"]:
            if field not in output_fields:
                output_fields.append(field)

        results = []
        for row in reader:
            base_row = dict(row)
            try:
                classified = classify_complaint(base_row)
            except Exception:
                classified = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Insufficient description to determine issue type.",
                    "flag": REVIEW_REQUIRED,
                }

            base_row["category"] = classified["category"]
            base_row["priority"] = classified["priority"]
            base_row["reason"] = classified["reason"]
            base_row["flag"] = classified["flag"]
            results.append(base_row)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
