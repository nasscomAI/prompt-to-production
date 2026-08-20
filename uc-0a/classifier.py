"""
UC-0A - Complaint Classifier

Deterministic classifier for the allowed complaint taxonomy.
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

CATEGORY_PATTERNS = {
    "Pothole": (
        "pothole",
        "potholes",
    ),
    "Flooding": (
        "flooded",
        "floods",
        "flooding",
        "knee-deep",
        "rainwater",
        "stranded",
        "water",
    ),
    "Streetlight": (
        "streetlight",
        "streetlights",
        "lamp post",
        "lights out",
        "unlit",
        "darkness",
        "dark at night",
        "sparking",
        "wiring",
    ),
    "Waste": (
        "garbage",
        "waste",
        "bins",
        "dead animal",
        "not cleared",
        "dumped",
        "overflowing",
        "piles",
    ),
    "Noise": (
        "music",
        "drilling",
        "amplifiers",
        "band playing",
        "audible",
        "midnight",
        "2am",
        "5am",
        "idling",
        "engines on",
    ),
    "Road Damage": (
        "road surface",
        "surface cracked",
        "surface buckled",
        "buckled",
        "collapsed",
        "cracked",
        "sinking",
        "subsidence",
        "subsided",
        "crater",
        "footpath",
        "tiles broken",
        "paving",
        "cobblestones",
        "bridge approach",
    ),
    "Heritage Damage": (
        "heritage",
        "historic",
        "ancient",
        "tagore museum",
        "victoria",
        "marble palace",
        "defaced",
        "old city",
    ),
    "Heat Hazard": (
        "heat",
        "heatwave",
        "44",
        "45",
        "52",
        "melting",
        "dangerous temperatures",
        "full sun",
        "unbearable",
        "burns",
        "exposed",
    ),
    "Drain Blockage": (
        "drain blocked",
        "drain completely blocked",
        "drain 100% blocked",
        "main drain blocked",
        "stormwater drain",
        "construction debris",
        "mosquito breeding",
        "manhole cover missing",
        "drain",
    ),
}

CATEGORY_ORDER = (
    "Pothole",
    "Drain Blockage",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Heat Hazard",
    "Heritage Damage",
    "Road Damage",
)

FIELDNAMES = ("complaint_id", "category", "priority", "reason", "flag")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def _contains_term(text: str, term: str) -> bool:
    if re.fullmatch(r"[a-z0-9]+", term):
        return re.search(rf"\b{re.escape(term)}\b", text) is not None
    return term in text


def _matching_terms(description: str) -> dict:
    matches = {}
    for category, terms in CATEGORY_PATTERNS.items():
        found = [term for term in terms if _contains_term(description, term)]
        if found:
            matches[category] = found
    return matches


def _choose_category(matches: dict) -> tuple[str, bool, list[str]]:
    if not matches:
        return "Other", True, []

    if len(matches) == 1:
        category = next(iter(matches))
        return category, False, matches[category]

    # Drain blockage often explains flooding; prefer it only when blockage words
    # are explicit and flooding is the only competing infrastructure symptom.
    if "Drain Blockage" in matches and set(matches).issubset({"Drain Blockage", "Flooding"}):
        return "Drain Blockage", False, matches["Drain Blockage"]

    for category in CATEGORY_ORDER:
        if category in matches:
            return category, True, matches[category]

    return "Other", True, []


def _severity_terms(description: str) -> list[str]:
    return [term for term in SEVERITY_KEYWORDS if term in description]


def _sentence_from_terms(terms: list[str], fallback: str) -> str:
    evidence = terms[:3] if terms else [fallback]
    quoted = ", ".join(f'"{term}"' for term in evidence)
    return f"Classified from description words {quoted}."


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint row into complaint_id, category, priority, reason, flag.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    raw_description = (row.get("description") or "").strip()
    description = _normalize(raw_description)

    if not raw_description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": 'Classified from description words "missing description".',
            "flag": "NEEDS_REVIEW",
        }

    matches = _matching_terms(description)
    category, ambiguous, category_terms = _choose_category(matches)
    severity_terms = _severity_terms(description)
    priority = "Urgent" if severity_terms else "Standard"

    reason_terms = severity_terms or category_terms
    reason = _sentence_from_terms(reason_terms, raw_description[:40])

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write a results CSV.

    Bad rows are emitted as NEEDS_REVIEW rows instead of stopping the batch.
    """
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for index, row in enumerate(reader, start=1):
            try:
                rows.append(classify_complaint(row))
            except Exception as exc:  # keep batch output complete for malformed rows
                rows.append(
                    {
                        "complaint_id": (row.get("complaint_id") or f"row-{index}").strip(),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f'Classified from description words "row error: {exc}".',
                        "flag": "NEEDS_REVIEW",
                    }
                )

    output = Path(output_path)
    if output.parent and str(output.parent) != ".":
        output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
