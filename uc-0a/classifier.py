"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re
from pathlib import Path

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

# Ordered rules: first matching category with the highest score wins.
# Keywords are matched case-insensitively as whole words or phrases.
CATEGORY_RULES = (
    ("Heat Hazard", ("heat", "temperature", "°c", "melting", "burns", "hot metal", "unbearable")),
    ("Heritage Damage", ("heritage", "historic", "ancient", "cobblestones", "step well", "museum", "tram road")),
    ("Drain Blockage", ("drain blocked", "drain completely blocked", "main drain blocked", "stormwater drain")),
    ("Flooding", ("flooded", "flooding", "floods", "knee-deep", "stranded", "rainwater channel")),
    ("Streetlight", ("streetlight", "streetlights", "lights out", "unlit", "darkness", "flickering", "lamp post", "wiring theft", "substation tripped")),
    ("Waste", ("garbage", "waste", "bins overflowing", "dead animal", "bulk waste", "overflowing", "dumped")),
    ("Noise", ("music", "drilling", "amplifiers", "noise", "idling", "engines on", "playing past midnight")),
    ("Pothole", ("pothole", "potholes")),
    ("Road Damage", ("road surface", "subsidence", "collapsed", "manhole", "footpath", "buckled", "sinking", "crater", "cracked", "missing cover", "tiles broken", "upturned")),
)


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _contains_keyword(text: str, keyword: str) -> bool:
    if " " in keyword:
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def _find_cited_words(description: str, keywords: tuple[str, ...]) -> list[str]:
    cited = []
    lower = _normalize(description)
    for keyword in keywords:
        if _contains_keyword(lower, keyword):
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            match = pattern.search(description)
            if match:
                cited.append(match.group(0))
    return cited


def _score_categories(description: str) -> dict[str, int]:
    lower = _normalize(description)
    scores: dict[str, int] = {name: 0 for name in ALLOWED_CATEGORIES}

    for category, keywords in CATEGORY_RULES:
        matched = {keyword for keyword in keywords if _contains_keyword(lower, keyword)}
        scores[category] = len(matched)

    return scores


def _pick_category(description: str) -> tuple[str, str, list[str]]:
    scores = _score_categories(description)
    ranked = sorted(
        ((cat, score) for cat, score in scores.items() if cat != "Other" and score > 0),
        key=lambda item: (-item[1], item[0]),
    )

    if not ranked:
        return "Other", "NEEDS_REVIEW", []

    top_score = ranked[0][1]
    top_categories = [cat for cat, score in ranked if score == top_score]

    if len(top_categories) > 1:
        return "Other", "NEEDS_REVIEW", _find_cited_words(description, tuple(
            kw for _, keywords in CATEGORY_RULES for kw in keywords
        ))

    category = top_categories[0]
    cited = []
    for cat, keywords in CATEGORY_RULES:
        if cat == category:
            cited = _find_cited_words(description, keywords)
            break

    return category, "", cited


def _priority(description: str) -> str:
    lower = _normalize(description)
    for keyword in SEVERITY_KEYWORDS:
        if _contains_keyword(lower, keyword):
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, cited: list[str], flag: str) -> str:
    if not description.strip():
        return "Description is missing so the complaint cannot be classified from available text."

    if flag == "NEEDS_REVIEW" and category == "Other":
        if cited:
            words = ", ".join(f'"{word}"' for word in cited[:3])
            return f"Description mentions {words} but the category remains genuinely ambiguous."
        return "Description does not clearly match a single allowed category."

    if cited:
        words = ", ".join(f'"{word}"' for word in cited[:3])
        return f'Classified as {category} because the description mentions {words}.'

    snippet = description.strip()
    if len(snippet) > 60:
        snippet = snippet[:60].rstrip() + "..."
    return f'Classified as {category} based on words in the description: "{snippet}".'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "") or ""

    if not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing so the complaint cannot be classified from available text.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag, cited = _pick_category(description)
    priority = _priority(description)
    reason = _build_reason(description, category, cited, flag)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write results CSV."""
    input_file = Path(input_path)
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"Input file has no header row: {input_path}")

        rows = list(reader)

    output_rows = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "category": "Other",
                "priority": "Low",
                "reason": "Classification failed for this row due to an unexpected processing error.",
                "flag": "NEEDS_REVIEW",
            }

        for field in ("category", "priority", "reason", "flag"):
            if field not in result or result[field] is None:
                raise ValueError(f"Missing required classification field '{field}' for row {row.get('complaint_id', '?')}")

        output_row = dict(row)
        output_row.update(result)
        output_rows.append(output_row)

    fieldnames = list(rows[0].keys()) if rows else []
    for field in ("category", "priority", "reason", "flag"):
        if field not in fieldnames:
            fieldnames.append(field)

    with Path(output_path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
