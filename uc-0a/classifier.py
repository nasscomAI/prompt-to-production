"""
UC-0A — Complaint Classifier.

Implements the two skills from skills.md (classify_complaint, batch_classify)
under the enforcement rules in agents.md:
  - category is exactly one of the 10 allowed strings (never a variation)
  - priority is Urgent iff a severity keyword appears in the description
  - reason is exactly one sentence quoting specific words from the description
  - flag is NEEDS_REVIEW iff the category cannot be decided from the
    description alone (multiple categories match or none match)
  - unmappable descriptions become category: Other, flag: NEEDS_REVIEW
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = (
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
)

SEVERITY_KEYWORDS = (
    "injury", "child", "school", "hospital", "ambulance", "fire",
    "hazard", "fell", "collapse",
)

_CATEGORY_PATTERNS = {
    "Pothole": (r"\bpotholes?\b",),
    "Flooding": (
        r"\bflood(?:ed|s)?\b", r"knee[- ]deep", r"standing in water",
        r"waterlog", r"submerg", r"inundat", r"channel rainwater",
    ),
    "Streetlight": (
        r"streetlight", r"street light", r"lights? out", r"unlit",
        r"\bdark(?:ness)?\b", r"\blamp", r"flicker", r"substation",
        r"wiring theft",
    ),
    "Waste": (
        r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"dead animal",
        r"\bbins?\b", r"\brubbish\b",
    ),
    "Noise": (
        r"\bnoise\b", r"\bmusic\b", r"\bband\b", r"\bamplifier",
        r"\bdrilling\b", r"\bidling\b", r"\bloud\b",
    ),
    "Road Damage": (
        r"\bmanhole\b", r"\bfootpath\b", r"upturned paving",
        r"\bcobblestone", r"\bcrater\b", r"\bcracked\b",
        r"\bsinking\b", r"\bbuckled\b", r"\bsubsid(?:ed|ence)\b",
        r"road collapsed",
        r"road surface (?:cracked|sinking|buckled|subsided)",
        r"tiles?\s+(?:broken|upturned)",
    ),
    "Heat Hazard": (
        r"\bheat", r"\bmelting\b", r"\bbubbling\b",
        r"\bunbearable\b", r"\bburn", r"full sun",
        r"\btemperature", r"\b°c\b",
    ),
    "Drain Blockage": (r"\bdrain",),
}

_HERITAGE_WORDS = ("heritage", "historic", "ancient", "museum")
_HERITAGE_DAMAGE_WORDS = (
    "knocked over", "knocked", "broken", "defaced", "not replaced",
    "subsidence", "subsided", "damaged", "damage",
    "cracked", "buckled",
)

_LOW_PATTERNS = (r"dead animal", r"grass dying", r"dying in heatwave")

_COMPILED = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
    for cat, pats in _CATEGORY_PATTERNS.items()
}
_LOW_COMPILED = [re.compile(p, re.IGNORECASE) for p in _LOW_PATTERNS]


def _first_matches(text: str) -> dict:
    """Earliest match per category -> {category: (quoted_text, position)}."""
    hits = {}
    lower = text.lower()
    for category, patterns in _COMPILED.items():
        best = None
        for pattern in patterns:
            m = pattern.search(text)
            if m and (best is None or m.start() < best[1]):
                best = (m.group(0), m.start())
        if best:
            hits[category] = best

    heritage_word = next((w for w in _HERITAGE_WORDS if w in lower), None)
    damage_word = next((w for w in _HERITAGE_DAMAGE_WORDS if w in lower), None)
    if heritage_word and damage_word:
        pos = lower.find(heritage_word)
        quote = text[pos:pos + len(heritage_word)]
        if "Heritage Damage" not in hits or pos < hits["Heritage Damage"][1]:
            hits["Heritage Damage"] = (quote, pos)
    return hits


def _priority(description: str) -> str:
    lower = description.lower()
    if any(k in lower for k in SEVERITY_KEYWORDS):
        return "Urgent"
    if any(p.search(description) for p in _LOW_COMPILED):
        return "Low"
    return "Standard"


def _quote_phrase(description: str) -> str:
    text = description.strip()
    end = text.find(".")
    if end != -1:
        text = text[:end]
    text = text.strip()
    if len(text) > 48:
        text = text[:45].rstrip() + "..."
    return text


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row -> complaint_id, category, priority, reason, flag."""
    if not isinstance(row, dict):
        return {
            "complaint_id": "", "category": "Other", "priority": "Standard",
            "reason": "No description was provided, so the complaint is flagged NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = row.get("complaint_id") or ""
    description = row.get("description")

    if description is None or not str(description).strip():
        return {
            "complaint_id": complaint_id, "category": "Other", "priority": "Standard",
            "reason": "No description was provided, so the complaint is flagged NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
        }
    if not isinstance(description, str):
        description = str(description)

    hits = _first_matches(description)

    if not hits:
        return {
            "complaint_id": complaint_id, "category": "Other",
            "priority": _priority(description),
            "reason": (f'The description "{_quote_phrase(description)}" maps to no allowed '
                       "category, so it is flagged NEEDS_REVIEW."),
            "flag": "NEEDS_REVIEW",
        }

    categories = sorted(hits, key=lambda c: hits[c][1])

    if len(categories) == 1:
        category = categories[0]
        reason = f'The description mentions "{hits[category][0]}", so this is classified as {category}.'
        return {
            "complaint_id": complaint_id, "category": category,
            "priority": _priority(description), "reason": reason, "flag": "",
        }

    category = categories[0]
    quotes = [hits[c][0] for c in categories[:2]]
    if len(categories) == 2:
        reason = (f'The description mentions both "{quotes[0]}" and "{quotes[1]}", so the '
                  "category cannot be decided from the description alone and is flagged NEEDS_REVIEW.")
    else:
        reason = (f'The description mentions "{quotes[0]}" and other categories, so the '
                  "category cannot be decided from the description alone and is flagged NEEDS_REVIEW.")
    return {
        "complaint_id": complaint_id, "category": category,
        "priority": _priority(description), "reason": reason, "flag": "NEEDS_REVIEW",
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV, print the row count."""
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if row is None:
                continue
            try:
                out = classify_complaint(row)
            except Exception:
                out = {
                    "complaint_id": row.get("complaint_id") or str(i + 1),
                    "category": "Other", "priority": "Standard",
                    "reason": "The row could not be processed, so it is flagged NEEDS_REVIEW.",
                    "flag": "NEEDS_REVIEW",
                }
            if not out.get("complaint_id"):
                out["complaint_id"] = str(i + 1)
            rows.append(out)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Classified {len(rows)} rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
