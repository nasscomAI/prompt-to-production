"""
UC-0A — Complaint Classifier

Classifies civic complaints into the exact workshop taxonomy.
Rules (from agents.md / README):
  * category must be one of the allowed taxonomy strings — no variations
  * priority is Urgent when a severity keyword is present, else Standard
  * every row carries a reason citing specific words from the description
  * genuinely ambiguous complaints get category + flag=NEEDS_REVIEW
  * complaints with no category match fall back to Other + NEEDS_REVIEW
"""
import argparse
import csv
import re

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

# Substring stems — must trigger Urgent when found in the description.
SEVERITY_KEYWORDS = [
    "injur", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collaps",
]

# Word-boundary keywords per category. Plurals/variants listed explicitly so
# \b...\b matching never misfires on partial words (e.g. "sun" vs "Sunday").
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "craters", "manhole", "manholes"],
    "Flooding": [
        "flood", "floods", "flooded", "flooding", "waterlogged",
        "submerged", "knee-deep", "inundat", "rainwater",
    ],
    "Streetlight": [
        "streetlight", "streetlights", "street light", "street lights",
        "lights out", "unlit", "lamp", "lamps", "lamp post", "lamp posts",
        "dark", "darkness", "substation", "lighting",
    ],
    "Waste": [
        "garbage", "waste", "bins", "bin", "refuse", "dead animal",
        "rubbish", "overflow", "overflowing",
    ],
    "Noise": [
        "music", "noise", "loud", "amplifier", "amplifiers", "drilling",
        "idling", "wedding", "band", "bands", "engine", "engines",
        "club", "clubs",
    ],
    "Road Damage": [
        "road surface", "road surfaces", "cracked", "buckled", "subsided",
        "sinking", "paving", "footpath", "footpaths", "cobblestones",
        "road collapsed", "road subsided", "utility work",
    ],
    "Heritage Damage": [
        "heritage", "heritage street", "historic", "ancient", "museum",
        "old city", "step well",
    ],
    "Heat Hazard": [
        "heat", "heatwave", "temperature", "temperatures", "melting",
        "bubbling", "°c", "burns", "sun",
    ],
    "Drain Blockage": [
        "drain", "drains", "drained", "draining", "stormwater",
        "mosquito", "drainage", "sewage",
    ],
}

# Tie-break order for genuinely ambiguous rows (the flagged category).
CATEGORY_ORDER = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage",
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _text_of(row: dict) -> str:
    """Combine every usable field so location context informs classification."""
    parts = [
        str(row.get("description", "")),
        str(row.get("location", "")),
        str(row.get("ward", "")),
        str(row.get("reported_by", "")),
    ]
    return " ".join(parts).lower()


def _find_keywords(text: str, keywords):
    found = []
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            found.append(kw)
    return found


def _severity_keyword(description: str) -> str:
    low = (description or "").lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in low:
            return kw
    return ""


def _best_category(text: str):
    """Return (chosen_category, matched_breakdown, ambiguous_bool).

    Scores every category by keyword hits. A tie between the top candidates,
    or a total absence of matches, marks the row as genuinely ambiguous.
    """
    scores = {}
    matched = {}
    for cat in ALLOWED_CATEGORIES:
        if cat == "Other":
            continue
        hits = _find_keywords(text, CATEGORY_KEYWORDS[cat])
        matched[cat] = hits
        scores[cat] = len(hits)

    ranked = sorted(
        (cat for cat in CATEGORY_ORDER if scores[cat] > 0),
        key=lambda c: scores[c],
        reverse=True,
    )

    if not ranked:
        return "Other", {}, True

    top = ranked[0]
    top_score = scores[top]

    # Ambiguous if any other category ties with the top score.
    tied = [c for c in ranked[1:] if scores[c] == top_score]
    ambiguous = len(tied) > 0

    breakdown = {c: matched[c] for c in ranked}
    return top, breakdown, ambiguous


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip() or "UNKNOWN"
    description = str(row.get("description", "")).strip()
    text = _text_of(row)

    category, breakdown, ambiguous = _best_category(text)

    sev = _severity_keyword(description)
    priority = "Urgent" if sev else "Standard"

    flag = "NEEDS_REVIEW" if ambiguous or category == "Other" else ""

    if category == "Other":
        reason = ("No taxonomy keyword matched the description; "
                  "category is genuinely ambiguous.")
    elif ambiguous:
        pair = []
        for c in sorted(breakdown.keys(), key=lambda x: scores_order(x)):
            hits = breakdown[c]
            if hits:
                pair.append(f"'{hits[0]}' ({c})")
        reason = ("Description matches " + " and ".join(pair) +
                  "; category is genuinely ambiguous.")
    else:
        kw = breakdown[category][0]
        reason = f"Description contains '{kw}' which matches category {category}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def scores_order(category: str) -> int:
    if category in CATEGORY_ORDER:
        return CATEGORY_ORDER.index(category)
    return len(CATEGORY_ORDER)


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never let one bad row kill the run
                result = {
                    "complaint_id": str(row.get("complaint_id", "")).strip() or "UNKNOWN",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error ({exc}); requires manual review.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")