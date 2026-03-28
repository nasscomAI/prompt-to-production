"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in agents.md and skills.md.
"""
import argparse
import csv
import re

# Enforcement: exact allowed category strings (agents.md)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Enforcement: keywords that must trigger Urgent priority (agents.md / README)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword map — ordered from most specific to least specific
CATEGORY_KEYWORDS = [
    (
        "Heritage Damage",
        [
            "heritage", "monument", "historical", "historic", "old city",
            "museum", "cobblestones", "defaced", "heritage stone", "step well",
        ],
    ),
    (
        "Heat Hazard",
        [
            "heat", "temperature", "hot", "summer", "heatwave", "sun",
            "burn", "burns", "unbearable", "melting",
        ],
    ),
    ("Drain Blockage",   ["drain", "drainage", "sewer", "stormwater", "manhole"]),
    (
        "Flooding",
        [
            "flood", "flooded", "flooding", "waterlog", "submerged", "standing in water",
            "rainwater", "inaccessible",
        ],
    ),
    ("Pothole",          ["pothole", "potholes"]),
    (
        "Road Damage",
        [
            "road collapse", "road collapsed", "crater", "road damage", "road cracked",
            "sinking", "subsidence", "subsided", "buckled", "surface cracked",
            "footpath broken", "tiles broken", "upturned", "paving removed",
        ],
    ),
    (
        "Streetlight",
        [
            "streetlight", "street light", "lamp", "lighting", "light not working",
            "lights out", "unlit", "very dark", "dark at night", "darkness",
        ],
    ),
    (
        "Waste",
        [
            "waste", "garbage", "trash", "rubbish", "litter", "dump", "debris",
            "overflowing", "dead animal", "bins",
        ],
    ),
    (
        "Noise",
        [
            "noise", "drilling", "loud", "sound", "idling", "honking", "music",
            "band", "amplifiers", "engines on",
        ],
    ),
]

HERITAGE_GENERIC_HINTS = {"heritage", "historic", "historical", "old city"}


def _contains_keyword(text: str, keyword: str) -> bool:
    """Match keyword as a standalone token/phrase to reduce false positives."""
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text) is not None


def _contains_severity_keyword(text: str, keyword: str) -> bool:
    """Match severity keywords with light inflection support (e.g., collapse -> collapsed)."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return any(token.startswith(keyword) for token in tokens)


def classify_complaint(row: dict) -> dict:
    """
    skill: classify_complaint
    Classifies a single complaint row into category, priority, reason, and flag.
    Input:  dict with at least a 'description' key.
    Output: dict with keys category, priority, reason, flag (plus original fields).
    """
    description = (row.get("description") or "").strip()

    # Error handling: missing or empty description
    if not description:
        return {
            **row,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Determine priority — Urgent if any severity keyword present
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if _contains_severity_keyword(desc_lower, kw)]
    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Determine category from all matching keyword groups, then disambiguate
    matched_by_category = {}
    for cat, keywords in CATEGORY_KEYWORDS:
        matched = [kw for kw in keywords if _contains_keyword(desc_lower, kw)]
        if matched:
            matched_by_category[cat] = matched

    category = None
    matched_keyword = None

    if matched_by_category:
        categories = set(matched_by_category.keys())

        # If both Flooding and Pothole appear, favor Pothole when explicitly present.
        if {"Flooding", "Pothole"}.issubset(categories):
            category = "Pothole"
            matched_keyword = matched_by_category["Pothole"][0]

        # If both Flooding and Drain Blockage appear, favor Drain Blockage.
        elif {"Flooding", "Drain Blockage"}.issubset(categories):
            category = "Drain Blockage"
            matched_keyword = matched_by_category["Drain Blockage"][0]

        # Heritage mentions are often contextual. If heritage is only generic and
        # another concrete civic category also matches, favor the concrete category.
        elif "Heritage Damage" in categories and len(categories) > 1:
            heritage_hits = set(matched_by_category["Heritage Damage"])
            category_order = [cat for cat, _ in CATEGORY_KEYWORDS]
            non_heritage_categories = [
                c for c in category_order if c in categories and c != "Heritage Damage"
            ]
            if heritage_hits.issubset(HERITAGE_GENERIC_HINTS):
                category = non_heritage_categories[0]
                matched_keyword = matched_by_category[category][0]

        # Otherwise, choose the strongest category by number of keyword hits.
        if category is None:
            sorted_candidates = sorted(
                matched_by_category.items(),
                key=lambda item: (len(item[1]), max(len(k) for k in item[1])),
                reverse=True,
            )

            # If top two are equally strong, mark ambiguous.
            if (
                len(sorted_candidates) > 1
                and len(sorted_candidates[0][1]) == len(sorted_candidates[1][1])
                and max(len(k) for k in sorted_candidates[0][1]) == max(len(k) for k in sorted_candidates[1][1])
            ):
                category = None
            else:
                category = sorted_candidates[0][0]
                matched_keyword = sorted_candidates[0][1][0]

    # Ambiguity handling
    if category is None:
        cited_text = " ".join(description.split()[:8])
        return {
            **row,
            "category": "Other",
            "priority": priority,
            "reason": f"Category is ambiguous based on '{cited_text}' in description.",
            "flag": "NEEDS_REVIEW",
        }

    if category not in ALLOWED_CATEGORIES:
        return {
            **row,
            "category": "Other",
            "priority": priority,
            "reason": f"Mapped category '{category}' is invalid for allowed schema.",
            "flag": "NEEDS_REVIEW",
        }

    if priority not in ALLOWED_PRIORITIES:
        return {
            **row,
            "category": "Other",
            "priority": "Low",
            "reason": "Computed priority is invalid for allowed schema.",
            "flag": "NEEDS_REVIEW",
        }

    # Build reason citing specific words from description (enforcement rule)
    reason = (
        f"Classified as {category} based on '{matched_keyword}' in description"
        + (f"; priority set to Urgent due to '{matched_severity[0]}'" if matched_severity else "")
        + "."
    )

    return {
        **row,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    skill: batch_classify
    Reads input CSV, applies classify_complaint per row, writes results CSV.
    Does not crash on bad rows — records classification errors inline.
    """
    output_extra_fields = ["category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []
        fieldnames = list(dict.fromkeys(input_fields + output_extra_fields))
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:
            results.append({
                **row,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {exc}",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
