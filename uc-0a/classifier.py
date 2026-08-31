"""
UC-0A — Complaint Classifier
Implements agents.md and skills.md enforcement rules.
"""
import argparse
import csv

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

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
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": [
        "flooded",
        "flooding",
        "floods",
        "flood",
        "knee-deep",
        "waterlogged",
        "standing in water",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "lights out",
        "unlit",
        "flickering",
        "sparking",
        "very dark",
    ],
    "Waste": [
        "garbage",
        "waste",
        "dead animal",
        "overflowing",
        "bins",
        "dumped",
    ],
    "Noise": ["music", "noise", "drilling", "amplifier", "wedding"],
    "Road Damage": [
        "cracked",
        "sinking",
        "buckled",
        "manhole",
        "footpath",
        "tiles broken",
        "upturned",
        "subsidence",
        "road surface",
    ],
    "Heritage Damage": ["heritage", "cobblestone", "historic", "lamp post"],
    "Heat Hazard": ["melting", "°c", "temperature", "heat", "burns", "hot"],
    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "drain blockage",
        "stormwater drain",
    ],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

AMBIGUOUS_PAIRS = [
    frozenset({"Heritage Damage", "Streetlight"}),
    frozenset({"Flooding", "Drain Blockage"}),
]


def _normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _find_severity_keywords(description: str) -> list[str]:
    desc_lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]


def _score_categories(description: str) -> tuple[dict[str, int], dict[str, list[str]]]:
    desc_lower = description.lower()
    scores: dict[str, int] = {}
    matches: dict[str, list[str]] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            scores[category] = len(matched)
            matches[category] = matched

    if "drain" in desc_lower and "block" in desc_lower:
        scores["Drain Blockage"] = scores.get("Drain Blockage", 0) + 2
        drain_matches = matches.setdefault("Drain Blockage", [])
        if "drain blocked" not in drain_matches:
            drain_matches.append("drain blocked")

    return scores, matches


def _has_drain_blockage_signal(description: str) -> bool:
    desc_lower = description.lower()
    return "drain" in desc_lower and "block" in desc_lower


def _is_ambiguous(scores: dict[str, int], description: str) -> tuple[bool, list[str]]:
    if not scores:
        return True, []

    if _has_drain_blockage_signal(description) and scores.get("Drain Blockage", 0) > 0:
        return False, ["Drain Blockage"]

    max_score = max(scores.values())
    top_categories = sorted(cat for cat, score in scores.items() if score == max_score)

    if len(top_categories) > 1:
        top_set = frozenset(top_categories)
        for pair in AMBIGUOUS_PAIRS:
            if pair.issubset(top_set):
                return True, top_categories

    desc_lower = description.lower()
    heritage_signal = "heritage" in desc_lower
    lighting_signal = any(
        phrase in desc_lower
        for phrase in ("lights out", "streetlight", "streetlights", "unlit")
    )
    if heritage_signal and lighting_signal:
        return True, ["Heritage Damage", "Streetlight"]

    return False, top_categories


def _resolve_category(scores: dict[str, int], description: str) -> tuple[str, list[str], bool]:
    ambiguous, candidates = _is_ambiguous(scores, description)
    if ambiguous:
        return "Other", candidates, True

    if not scores:
        return "Other", [], True

    max_score = max(scores.values())
    winners = [cat for cat, score in scores.items() if score == max_score]

    if len(winners) == 1:
        return winners[0], winners, False

    desc_lower = description.lower()
    if "Drain Blockage" in winners and "drain" in desc_lower and "block" in desc_lower:
        return "Drain Blockage", ["Drain Blockage"], False

    return "Other", winners, True


def _extract_cited_phrase(description: str, matched_keywords: list[str]) -> str:
    if not matched_keywords:
        snippet = description[:80].strip(" ,.;")
        return snippet if snippet else description

    desc_lower = description.lower()
    for keyword in sorted(matched_keywords, key=len, reverse=True):
        idx = desc_lower.find(keyword)
        if idx == -1:
            continue
        start = max(0, description.rfind(" ", 0, max(idx - 10, 0)))
        if start == 0 and idx > 0:
            start = 0
        end = min(len(description), idx + len(keyword) + 30)
        phrase = description[start:end].strip(" ,.;")
        if phrase:
            return phrase

    return description[:80].strip(" ,.;")


def _build_reason(
    description: str,
    category: str,
    priority: str,
    severity_matches: list[str],
    category_matches: list[str],
    ambiguous: bool,
    ambiguous_candidates: list[str],
) -> str:
    cited = _extract_cited_phrase(description, category_matches or severity_matches)

    if ambiguous and ambiguous_candidates:
        candidate_text = " and ".join(ambiguous_candidates)
        return (
            f"Description mentions '{cited}', making {candidate_text} equally plausible, "
            f"so category is Other with NEEDS_REVIEW and priority is {priority}."
        )

    if severity_matches:
        severity_text = "', '".join(severity_matches)
        if category_matches:
            return (
                f"Description cites '{cited}' and contains '{severity_text}', "
                f"so category is {category} and priority is Urgent."
            )
        return (
            f"Description contains '{severity_text}', so priority is Urgent "
            f"and category is {category} based on '{cited}'."
        )

    return (
        f"Description cites '{cited}' with no severity keywords, "
        f"so category is {category} and priority is {priority}."
    )


def _determine_priority(description: str) -> tuple[str, list[str]]:
    severity_matches = _find_severity_keywords(description)
    if severity_matches:
        return "Urgent", severity_matches
    return "Standard", []


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if row is None or not isinstance(row, dict):
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "Input row is missing or invalid, so classification requires review.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = _normalize_text(row.get("complaint_id"))
    description = _normalize_text(row.get("description"))

    if not complaint_id:
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "complaint_id is missing or empty, so classification requires review.",
            "flag": "NEEDS_REVIEW",
        }

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "description is missing or empty, so classification requires review.",
            "flag": "NEEDS_REVIEW",
        }

    priority, severity_matches = _determine_priority(description)
    scores, matches_by_category = _score_categories(description)
    category, candidates, ambiguous = _resolve_category(scores, description)
    category_matches = matches_by_category.get(category, [])

    if ambiguous:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_matches = []
        for candidate in candidates:
            category_matches.extend(matches_by_category.get(candidate, []))
    else:
        flag = ""

    reason = _build_reason(
        description,
        category,
        priority,
        severity_matches,
        category_matches,
        ambiguous,
        candidates,
    )

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
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {input_path}") from exc

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:
            complaint_id = _normalize_text(row.get("complaint_id") if isinstance(row, dict) else "")
            results.append(
                {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            )

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
