"""
UC-0A — Complaint Classifier

Implements the RICE enforcement rules from agents.md and the two skills from
skills.md: classify_complaint and batch_classify.
"""
import argparse
import csv
import re
import sys

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
    "injuries",
    "child",
    "children",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "hazards",
    "fell",
    "hospitalised",
    "hospitalized",
    "collapse",
    "collapsed",
]

CATEGORY_KEYWORDS = {
    "Heat Hazard": ["heat", "temperature", "temperatures", "melting", "burn", "burns"],
    "Heritage Damage": ["heritage"],
    "Pothole": ["pothole", "potholes"],
    "Drain Blockage": [
        "drain",
        "drains",
        "drainage",
        "blocked",
        "blockage",
        "manhole",
    ],
    "Flooding": ["flood", "floods", "flooded", "flooding", "rain", "water"],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "light",
        "lights",
        "lighting",
        "unlit",
        "dark",
        "darkness",
    ],
    "Waste": ["garbage", "waste", "bin", "bins", "animal", "animals", "dumped", "debris"],
    "Noise": [
        "noise",
        "noises",
        "music",
        "band",
        "bands",
        "amplifier",
        "amplifiers",
        "speakers",
        "construction",
        "drilling",
        "idling",
    ],
    "Road Damage": [
        "road surface",
        "cracked",
        "cracking",
        "sinking",
        "sunk",
        "subsidence",
        "paving",
        "footpath",
        "footpaths",
        "manhole",
    ],
}

LOCATION_KEYWORDS = {
    "Road Damage": ["road", "roads", "bridge", "bridges"],
}

CLASSIFICATION_FIELDS = ["category", "priority", "reason", "flag"]


def _matches(lowered: str, keyword: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}\b", lowered) is not None


def _matched_keywords(lowered: str, keywords: list) -> list:
    return [kw for kw in keywords if _matches(lowered, kw)]


def _score_keywords(text: str) -> list:
    scores = []
    lowered = text.lower()
    for category in ALLOWED_CATEGORIES:
        if category == "Other":
            continue
        hits = 0
        for keyword in CATEGORY_KEYWORDS.get(category, []):
            if _matches(lowered, keyword):
                hits += 2
        for keyword in LOCATION_KEYWORDS.get(category, []):
            if _matches(lowered, keyword):
                hits += 1
        scores.append((category, hits))
    return scores


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag.
    Category is one of the 10 allowed strings. Priority is Urgent/Standard/Low.
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": (
                "Category \"Other\": description is empty, no keywords to classify "
                "from; flag NEEDS_REVIEW."
            ),
            "flag": "NEEDS_REVIEW",
        }

    scores = [s for s in _score_keywords(description) if s[1] > 0]
    lowered = description.lower()

    urgent = any(_matches(lowered, kw) for kw in SEVERITY_KEYWORDS)

    if not scores:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": (
                "Category \"Other\": no classification keyword matches the "
                "description; cannot be determined from description alone."
            ),
            "flag": "NEEDS_REVIEW",
        }

    scores.sort(key=lambda item: item[1], reverse=True)
    best_category, best_score = scores[0]
    tied = any(score == best_score for _, score in scores[1:])

    cited = ", ".join(
        f'"{kw}"'
        for kw in _matched_keywords(lowered, CATEGORY_KEYWORDS.get(best_category, []))
    )

    if urgent:
        seen = _matched_keywords(lowered, SEVERITY_KEYWORDS)
        priority = "Urgent"
        cited_sev = ", ".join(f'"{kw}"' for kw in seen)
        reason = (
            f'Category "{best_category}": description mentions {cited}. '
            f'Priority "Urgent": description contains severity word(s) {cited_sev}.'
        )
    else:
        priority = "Standard"
        reason = (
            f'Category "{best_category}": description mentions {cited}. '
            'Priority "Standard": no severity keyword present.'
        )

    flag = "NEEDS_REVIEW" if tied else ""
    return {
        "complaint_id": complaint_id,
        "category": best_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read the city test CSV, classify every row, write the results CSV.

    Every input row is preserved and enriched with category, priority, reason,
    and flag. A missing input file or missing description column raises a clear
    error; individual bad rows are still written rather than dropped.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as in_file:
            reader = csv.DictReader(in_file)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no header row.")
            if "description" not in reader.fieldnames:
                raise ValueError(
                    f'Missing required column "description" in {input_path}. '
                    "Cannot classify without a description."
                )
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except PermissionError:
        raise PermissionError(f"Cannot read input file: {input_path}")

    if not rows:
        raise ValueError(f"Input CSV is empty: {input_path}")

    enriched = []
    for row in rows:
        try:
            classified = classify_complaint(row)
        except Exception as exc:
            classified = {
                "complaint_id": row.get("complaint_id", "").strip(),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        out_row = dict(row)
        out_row.update({field: classified[field] for field in CLASSIFICATION_FIELDS})
        enriched.append(out_row)

    fieldnames = rows[0].keys()
    fieldnames = list(fieldnames) + [
        f for f in CLASSIFICATION_FIELDS if f not in fieldnames
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Results written to {args.output}")