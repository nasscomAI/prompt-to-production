"""
UC-0A — Complaint Classifier

Implements:
- classify_complaint: classify one complaint row
- batch_classify: classify all rows in an input CSV and write results

The implementation follows the UC-0A enforcement rules:
- Exact allowed category names
- Urgent severity keywords
- One-sentence reason citing words from the description
- NEEDS_REVIEW for genuine ambiguity
- Bad/null rows do not crash the batch
"""

import argparse
import csv
import re
from pathlib import Path


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


# More specific categories are checked before broader ones.
CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "pot hole",
        "potholes",
    ],

    "Flooding": [
        "flood",
        "flooding",
        "flooded",
        "waterlogged",
        "water logging",
        "waterlogging",
        "water accumulation",
        "standing water",
        "bridge floods",
        "bridge approach floods",
        "underpass floods",
        "underpass flooding",
        "underpass flooded",
    ],

    "Streetlight": [
        "streetlight",
        "streetlights",
        "street light",
        "street lights",
        "lamp post",
        "lamp posts",
        "lamp",
        "light pole",
        "light poles",
        "lights not working",
        "lights out",
        "street lighting",
        "unlit",
        "unlit area",
        "unlit street",
        "unlit colony",
        "unlit residential colony",
        "colony unlit",
    ],

    "Waste": [
        "garbage",
        "waste",
        "trash",
        "rubbish",
        "litter",
        "dumping",
        "dumped waste",
        "garbage collection",
        "dead animal",
        "animal carcass",
        "animal not removed",
        "dead animals",
    ],

    "Noise": [
        "noise",
        "noisy",
        "loud music",
        "music past midnight",
        "music after midnight",
        "music at 2am",
        "music at 2 am",
        "club music",
        "loudspeaker",
        "loud speaker",
        "sound pollution",
        "excessive noise",
        "noise pollution",
        "music audible",
        "music past",
        "construction drilling",
        "drilling",
        "drilling from 5am",
    ],

    "Road Damage": [
        "road damage",
        "damaged road",
        "broken road",
        "cracked road",
        "road crack",
        "road surface",
        "road condition",
        "road subsided",
        "subsided",
        "subsidence",
        "road subsidence",
        "damaged pavement",
        "broken pavement",
        "pavement damage",
        "footpath",
        "footpath tiles",
        "broken footpath",
        "upturned footpath",
        "broken tiles",
        "upturned paving",
        "upturned paving tiles",
        "broken paving",
        "broken bench",
        "damaged bench",
        "manhole cover",
        "missing manhole",
        "manhole missing",
        "open manhole",
        "road divider",
        "road dividers",
        "broken shelter",
        "shelter roof",
        "broken roof",
        "shelter glass",
        "broken glass",
        "bus shelter roof",
        "road collapsed",
        "road collapse",
        "partially collapsed road",
        "road crater",
        "crater",
    ],

    "Heritage Damage": [
        "heritage",
        "historical monument",
        "historic monument",
        "monument damage",
        "heritage site",
        "heritage building",
    ],

    "Heat Hazard": [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
        "hot weather hazard",
        "dangerous temperatures",
        "dangerous temperature",
        "high temperature",
        "high temperatures",
        "extreme temperature",
        "extreme temperatures",
        "temperature unbearable",
        "temperatures unbearable",
        "surface temperature",
        "surface temperatures",
        "surface temperature unbearable",
        "tarmac surface melting",
        "tarmac melting",
        "tarmac surface",
        "footwear sticking",
        "storing heat",
        "storing excessive heat",
        "metal storing heat",
        "metal road dividers storing heat",
    ],

    "Drain Blockage": [
        "blocked drain",
        "drain blockage",
        "drain blocked",
        "blocked drainage",
        "clogged drain",
        "drain clogged",
        "drainage blockage",
        "drainage blocked",
        "stormwater drain",
        "stormwater drain blocked",
        "stormwater drain 100% blocked",
    ],
}

def _normalise_text(value) -> str:
    """Return safely normalised text."""
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def _contains_keyword(text: str, keyword: str) -> bool:
    """Case-insensitive whole-word/phrase matching."""
    pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def _find_severity_keyword(description: str):
    """Return the first required severity keyword or its common word form."""
    text = description.lower()

    for keyword in SEVERITY_KEYWORDS:
        keyword = keyword.lower()

        # Exact keyword
        if _contains_keyword(text, keyword):
            return keyword

        # Common inflected forms, e.g. collapse -> collapsed/collapsing
        if keyword == "collapse":
            if (
                _contains_keyword(text, "collapsed")
                or _contains_keyword(text, "collapsing")
            ):
                return keyword

        if keyword == "injury":
            if _contains_keyword(text, "injuries"):
                return keyword

        if keyword == "child":
            if _contains_keyword(text, "children"):
                return keyword

    return None


def _find_category_matches(description: str):
    """
    Return all categories supported by explicit description keywords.

    A complaint matching multiple categories is treated as ambiguous unless
    one category is clearly supported by a more specific phrase.
    """
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        found = []

        for keyword in keywords:
            if _contains_keyword(description, keyword):
                found.append(keyword)

        if found:
            matches.append((category, found))

    return matches


def _build_reason(description: str, category: str, matched_words=None) -> str:
    """
    Build exactly one sentence and cite words from the description.

    The cited words are kept in quotation marks so the reason visibly points
    back to the original complaint description.
    """
    if matched_words:
        cited = ", ".join(f'"{word}"' for word in matched_words[:2])
        return f'The description mentions {cited}, supporting the category "{category}".'

    # For Other, cite a short portion of the actual description.
    words = description.split()

    if words:
        excerpt = " ".join(words[:8]).rstrip(".,!?;:")
        return f'The description states "{excerpt}", but it does not clearly match an allowed category.'

    return 'The description is empty, so the complaint cannot be classified from the provided information.'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns:
        dict with keys:
        complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint row is invalid and does not contain usable complaint information.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = _normalise_text(row.get("complaint_id"))
    description = _normalise_text(row.get("description"))

    # Invalid/missing description: cannot make a reliable classification.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is empty, so the complaint cannot be classified from the provided information.",
            "flag": "NEEDS_REVIEW",
        }

    # Priority is determined independently from category.
    severity_keyword = _find_severity_keyword(description)

    if severity_keyword:
        priority = "Urgent"
    else:
        priority = "Standard"

    matches = _find_category_matches(description)

    # No supported category evidence.
    if not matches:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _build_reason(description, "Other"),
            "flag": "NEEDS_REVIEW",
        }

    # More than one category is supported by the description.
    if len(matches) > 1:
        matched_categories = [category for category, _ in matches]

        cited_words = []
        for _, words in matches:
            cited_words.extend(words[:1])

        cited = ", ".join(f'"{word}"' for word in cited_words[:3])

        reason = (
            f'The description contains {cited}, which supports multiple allowed '
            f'categories ({", ".join(matched_categories)}).'
        )

        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": reason,
            "flag": "NEEDS_REVIEW",
        }

    # Exactly one category is supported.
    category, matched_words = matches[0]

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _build_reason(description, category, matched_words),
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.

    Bad/null rows are handled individually so one bad row does not prevent
    the remaining complaints from being processed.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    results = []

    try:
        with input_file.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                results.append(
                    {
                        "complaint_id": "",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "The input CSV has no header row to identify complaint fields.",
                        "flag": "NEEDS_REVIEW",
                    }
                )
            else:
                for row in reader:
                    try:
                        result = classify_complaint(row)
                    except Exception as exc:
                        result = {
                            "complaint_id": _normalise_text(row.get("complaint_id")),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f'The complaint could not be classified because of an input processing error: "{type(exc).__name__}".',
                            "flag": "NEEDS_REVIEW",
                        }

                    results.append(result)

    except FileNotFoundError:
        results.append(
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": f'The input file "{input_path}" could not be found.',
                "flag": "NEEDS_REVIEW",
            }
        )

    except Exception as exc:
        results.append(
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": f'The input file could not be processed because of "{type(exc).__name__}".',
                "flag": "NEEDS_REVIEW",
            }
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with output_file.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for result in results:
            # Final enforcement before writing.
            if result.get("category") not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"

            if result.get("priority") not in ALLOWED_PRIORITIES:
                result["priority"] = "Standard"
                result["flag"] = "NEEDS_REVIEW"

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_[city].csv",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")