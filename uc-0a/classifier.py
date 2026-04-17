"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
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
    "Pothole": ["pothole", "potholes", "crater"],
    "Flooding": [
        "flood",
        "flooded",
        "flooding",
        "waterlogged",
        "water-logged",
        "water logging",
        "waterlogging",
        "submerged",
        "knee-deep",
        "inundated",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "lights out",
        "light out",
        "flickering",
        "lamp post",
        "lamp-post",
        "dark at night",
    ],
    "Waste": [
        "garbage",
        "trash",
        "rubbish",
        "waste",
        "litter",
        "bin",
        "bins",
        "dumped",
        "dumping",
        "dead animal",
        "carcass",
    ],
    "Noise": [
        "noise",
        "loud",
        "music",
        "midnight",
        "dj",
        "speaker",
        "honking",
    ],
    "Road Damage": [
        "road damage",
        "road surface",
        "cracked",
        "sinking",
        "broken road",
        "upturned",
        "uneven road",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "historic",
        "historical",
        "protected structure",
        "vandal",
        "defaced",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "heat wave",
        "hot pavement",
        "dehydration",
        "sunstroke",
    ],
    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "clogged drain",
        "drainage blocked",
        "manhole",
        "sewer",
        "nala",
        "gutter",
    ],
}


def _get_description(row: dict) -> str:
    for field in ("description", "complaint_description", "details", "text"):
        value = row.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _get_complaint_id(row: dict) -> str:
    for field in ("complaint_id", "id", "case_id"):
        value = row.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _matches_keyword(text: str, keyword: str) -> bool:
    return keyword in text


def _detect_priority(text: str) -> str:
    for keyword in SEVERITY_KEYWORDS:
        if _matches_keyword(text, keyword):
            return "Urgent"
    return "Standard"


def _pick_category(text: str) -> tuple[str, list[str], bool]:
    category_hits: dict[str, list[str]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if _matches_keyword(text, kw)]
        if hits:
            category_hits[category] = hits

    # Heritage Damage requires an explicit damage cue, otherwise it is often
    # just a location reference and should not force the category.
    if "Heritage Damage" in category_hits:
        damage_cues = ["damage", "damaged", "crack", "broken", "collapse", "fell", "vandal", "defaced"]
        if not any(cue in text for cue in damage_cues):
            category_hits.pop("Heritage Damage")

    if not category_hits:
        return "Other", [], True

    top_score = max(len(hits) for hits in category_hits.values())
    top_categories = [cat for cat, hits in category_hits.items() if len(hits) == top_score]

    if len(top_categories) > 1:
        return "Other", [], True

    selected = top_categories[0]
    return selected, category_hits[selected], False


def _build_reason(category: str, matched_terms: list[str], priority: str, ambiguous: bool) -> str:
    if ambiguous:
        return "Category is unclear from the description text, so it is marked NEEDS_REVIEW."

    if matched_terms:
        term_fragment = f'"{matched_terms[0]}"'
    else:
        term_fragment = '"description"'

    if priority == "Urgent":
        return f'Classified as {category} because the description includes {term_fragment} and an urgent severity cue.'

    return f'Classified as {category} because the description includes {term_fragment}.'

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = _get_complaint_id(row)
    description = _get_description(row)
    text = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description text is missing, so classification requires review.",
            "flag": "NEEDS_REVIEW",
        }

    priority = _detect_priority(text)
    category, matched_terms, ambiguous = _pick_category(text)
    flag = "NEEDS_REVIEW" if ambiguous else ""
    reason = _build_reason(category, matched_terms, priority, ambiguous)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category could not be mapped to the allowed taxonomy and requires review."

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
    output_rows = []

    try:
        with open(input_path, mode="r", newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header row.")

            for row in reader:
                try:
                    output_rows.append(classify_complaint(row))
                except Exception as exc:  # noqa: BLE001
                    output_rows.append(
                        {
                            "complaint_id": _get_complaint_id(row),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Row could not be classified due to processing error: {str(exc)}.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {input_path}") from exc
    except csv.Error as exc:
        raise ValueError(f"Input CSV is malformed and could not be parsed: {str(exc)}") from exc
    except OSError as exc:
        raise OSError(f"Input file could not be read: {input_path}") from exc

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
