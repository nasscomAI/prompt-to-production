"""
UC-0A — Complaint Classifier
Built from agents.md / skills.md (RICE enforcement, CRAFT-tested).
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

# Phrase patterns scored per allowed category. Order inside a category is
# strongest evidence first. Patterns are case-insensitive.
CATEGORY_PATTERNS = {
    "Pothole": [
        r"pothole",
    ],
    "Flooding": [
        r"flood",
        r"knee-deep",
        r"standing in water",
        r"channel rainwater",
    ],
    "Drain Blockage": [
        r"drain(?:s|age)?\s+(?:completely\s+)?blocked",
        r"drain blocked",
        r"blocked with",
        r"main drain",
        r"stormwater drain",
        r"mosquito breeding",
    ],
    "Streetlight": [
        r"streetlights?",
        r"street light",
        r"lights? out",
        r"flickering",
        r"sparking",
        r"unlit",
        r"darkness",
        r"substation tripped",
        r"wiring theft",
        r"area very dark",
    ],
    "Waste": [
        r"garbage",
        r"bulk waste",
        r"waste bins",
        r"waste overflowing",
        r"waste not cleared",
        r"post-market waste",
        r"dead animal",
        r"dumped on public road",
        r"overflowing garbage",
        r"restaurant waste",
    ],
    "Noise": [
        r"playing music",
        r"club music",
        r"amplifiers?",
        r"construction drilling",
        r"idling with engines",
        r"wedding band",
    ],
    "Heritage Damage": [
        r"heritage lamp post knocked",
        r"historic tram road cobblestones broken",
        r"defaced",
        r"heritage stone not replaced",
        r"ancient step well",
        r"heritage concern",
    ],
    "Heat Hazard": [
        r"melting",
        r"heatwave",
        r"\d+\s*°\s*c",
        r"dangerous temperatures",
        r"temperature unbearable",
        r"storing heat",
        r"burns on contact",
        r"exposed to full sun",
        r"footwear sticking",
    ],
    "Road Damage": [
        r"road collapsed",
        r"road surface",
        r"road subsided",
        r"cracked and sinking",
        r"footpath",
        r"broken bench",
        r"upturned paving",
        r"tarmac surface",
        r"surface bubbling",
        r"surface buckled",
        r"crater",
        r"cobblestones broken",
        r"street paving removed",
    ],
}

OUTPUT_FIELDS = ("complaint_id", "category", "priority", "reason", "flag")


def _text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _find_severity_hits(description: str) -> list[str]:
    lowered = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in lowered]


def _pattern_hit(description: str, pattern: str):
    return re.search(pattern, description, flags=re.IGNORECASE)


def _score_categories(description: str) -> list[tuple[str, str]]:
    """Return (category, matched_span) for every category with evidence."""
    hits = []
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            match = _pattern_hit(description, pattern)
            if match:
                hits.append((category, match.group(0)))
                break
    return hits


def _choose_category(hits: list[tuple[str, str]]) -> tuple[str, str, bool]:
    """
    Returns (category, cited_span, ambiguous).
    Pothole outranks Road Damage. Flooding + Drain Blockage is always ambiguous.
    """
    if not hits:
        return "Other", "", True

    names = [name for name, _ in hits]
    unique_names = list(dict.fromkeys(names))

    if "Pothole" in unique_names and "Road Damage" in unique_names:
        unique_names = [n for n in unique_names if n != "Road Damage"]
        hits = [h for h in hits if h[0] != "Road Damage"]
    if "Heat Hazard" in unique_names and "Road Damage" in unique_names:
        unique_names = [n for n in unique_names if n != "Road Damage"]
        hits = [h for h in hits if h[0] != "Road Damage"]

    flood_drain = "Flooding" in unique_names and "Drain Blockage" in unique_names
    ambiguous = flood_drain or len(unique_names) > 1

    # Prefer the more specific civic object when two hits remain.
    preference = [
        "Pothole",
        "Heat Hazard",
        "Heritage Damage",
        "Drain Blockage",
        "Flooding",
        "Streetlight",
        "Waste",
        "Noise",
        "Road Damage",
        "Other",
    ]
    chosen = next((name for name in preference if name in unique_names), unique_names[0])
    cited = next(span for name, span in hits if name == chosen)
    return chosen, cited, ambiguous


def _priority(description: str, category: str, severity_hits: list[str]) -> str:
    if severity_hits:
        return "Urgent"
    if category == "Noise":
        return "Low"
    return "Standard"


def _quote_from_description(description: str, span: str) -> str:
    if span:
        return span
    words = description.split()
    return " ".join(words[:8]) if words else ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    try:
        if not isinstance(row, dict):
            row = {}
        complaint_id = _text(row.get("complaint_id")) or "UNKNOWN"
        description = _text(row.get("description"))

        if not description:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Standard",
                "reason": "Description is missing so category cannot be determined from the complaint text.",
                "flag": "NEEDS_REVIEW",
            }

        hits = _score_categories(description)
        category, cited, ambiguous = _choose_category(hits)
        severity_hits = _find_severity_hits(description)
        priority = _priority(description, category, severity_hits)
        quoted = _quote_from_description(description, cited)

        if not description:
            reason = "Description is missing so category cannot be determined from the complaint text."
        elif cited:
            reason = f"Classified as {category} because the description cites '{quoted}'."
        else:
            snippet = _quote_from_description(description, "")
            reason = (
                f"Classified as Other because no allowed-category keywords matched "
                f"the description starting '{snippet}'."
            )

        if severity_hits and priority == "Urgent":
            reason = reason.rstrip(".") + f", and priority is Urgent due to '{severity_hits[0]}'."

        flag = "NEEDS_REVIEW" if ambiguous else ""
        if category not in ALLOWED_CATEGORIES:
            category = "Other"
            flag = "NEEDS_REVIEW"

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except Exception as exc:  # noqa: BLE001 — must never crash a batch row
        return {
            "complaint_id": _text((row or {}).get("complaint_id")) if isinstance(row, dict) else "UNKNOWN",
            "category": "Other",
            "priority": "Standard",
            "reason": f"Row could not be classified because of an internal error ({type(exc).__name__}).",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, writes output even if some rows fail.
    """
    results = []
    with open(input_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=2):
            try:
                if row is None:
                    row = {}
                # DictReader can yield None values for missing cells.
                cleaned = {key: ("" if value is None else value) for key, value in (row or {}).items()}
                results.append(classify_complaint(cleaned))
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "complaint_id": f"ROW-{index}",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be classified because of an internal error ({type(exc).__name__}).",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
