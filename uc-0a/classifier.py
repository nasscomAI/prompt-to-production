"""
UC-0A — Complaint Classifier
Implements the rules in agents.md and the skills defined in skills.md.
"""
import argparse
import csv
import re
import sys

SCHEMA_CATEGORIES = [
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

SEVERITY_PATTERNS = [
    r"injur\w*",
    r"child\w*",
    r"school\w*",
    r"hospitals?",
    r"ambulances?",
    r"\bfire\b",
    r"hazard\w*",
    r"\bfell\b",
    r"collaps\w*",
]

CATEGORY_PATTERNS = {
    "Pothole": [r"potholes?"],
    "Flooding": [r"flood\w*", r"water[- ]?log(ged|ging)?", r"drain(age|ing)\b"],
    "Streetlight": [
        r"street ?lamps?",
        r"street ?lights?",
        r"lights? out",
        r"lamp ?posts?",
    ],
    "Waste": [
        r"garbage",
        r"wastes?",
        r"trash",
        r"rubbish",
        r"litter",
        r"dump(ed)?",
        r"dead animal",
        r"\bbins?\b",
        r"debris",
    ],
    "Noise": [r"nois(e|y)", r"\bloud\b", r"music", r"\bsounds?\b", r"\bband\b", r"amplifiers?", r"loudspeakers?", r"speakers?"],
    "Road Damage": [
        r"roads? (surface |is |are )*damage(d)?",
        r"road surface",
        r"crack(ed|s)?",
        r"sinking",
        r"cave[- ]?ins?",
        r"footpath",
        r"pavement",
        r"(tiles?|kerb|curb)[^.;]*(broken|upturned|loose)",
        r"upturned",
        r"cobblestones?[^.;]*(broken|uprooted|damaged)",
        r"subsid(e|ed|ence)",
        r"buckl(ed|e|ing)",
    ],
    "Heritage Damage": [r"heritage"],
    "Heat Hazard": [r"heat ?waves?", r"extreme heat", r"heat ?strokes?", r"temperatures?\b", r"\bmelting\b", r"storing heat", r"\bbubbl\w*\b"],
    "Drain Blockage": [
        r"(drains?|sewers?)[^.;]{0,40}(block\w*|clog\w*|chok\w*)",
        r"(block\w*|clog\w*|chok\w*)[^.;]{0,40}(drains?|sewers?)",
    ],
}

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id") or "").strip()
    description = str(row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty, so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    category_hits = _find_category_matches(description)
    severity_hits = _find_severity_matches(description)

    matched_categories = []
    evidence = {}
    for _, _, cat, snippet in category_hits:
        if cat not in evidence:
            matched_categories.append(cat)
            evidence[cat] = snippet

    multi_match = len(matched_categories) > 1
    flag = "NEEDS_REVIEW" if multi_match else ""

    if not matched_categories:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if severity_hits else "Standard",
            "reason": (
                f"No schema category keyword found in the description"
                + (
                    f', but severity word "{severity_hits[0]}" requires Urgent.'
                    if severity_hits
                    else ", so it is classified Other."
                )
            ),
            "flag": "NEEDS_REVIEW",
        }

    category = matched_categories[0]
    snippet = evidence[category]
    parts = matched_categories[:2] if multi_match else matched_categories

    if severity_hits:
        priority = "Urgent"
        reason = (
            f'Description cites "{snippet}" indicating {category}, '
            f'and severity word "{severity_hits[0]}" makes this Urgent'
        )
    elif category == "Noise":
        priority = "Low"
        reason = f'Description cites "{snippet}" indicating {category}, a nuisance with no severity keyword so priority is Low'
    else:
        priority = "Standard"
        reason = f'Description cites "{snippet}" indicating {category}, with no severity keyword so priority is Standard'

    if multi_match:
        reason += f"; multiple categories matched ({', '.join(parts)}), flagged NEEDS_REVIEW"

    reason += "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _find_category_matches(description: str):
    hits = []
    for order, category in enumerate(SCHEMA_CATEGORIES[:-1]):
        for pattern in CATEGORY_PATTERNS.get(category, []):
            match = re.search(pattern, description, flags=re.IGNORECASE)
            if match:
                hits.append((match.start(), order, category, match.group(0)))
    hits.sort(key=lambda h: (h[0], h[1]))
    return hits


def _find_severity_matches(description: str):
    hits = []
    for pattern in SEVERITY_PATTERNS:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            hits.append(match.group(0))
    return hits


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as infile:
            rows = list(csv.DictReader(infile))
    except FileNotFoundError:
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:
            results.append(
                {
                    "complaint_id": str(row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classifier error ({exc}); row needs manual review.",
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
