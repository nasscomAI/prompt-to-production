"""
UC-0A — Complaint Classifier
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Ordered by priority: earlier categories win when a description matches more
# than one. Order was chosen so specific, unambiguous signals (pothole, a
# named drain blockage) are checked before broader ones (heritage, noise).
# If more than one distinct category matches, classify_complaint still picks
# the first match but sets flag=NEEDS_REVIEW so a human resolves it, per
# agents.md enforcement rule 4.
CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "potholes"]),
    ("Drain Blockage", ["drain blocked", "drain completely blocked", "stormwater drain", "main drain"]),
    ("Flooding", ["flood", "flooded", "floods", "waterlogged", "knee-deep", "channel rainwater"]),
    ("Heat Hazard", ["°c", "melting", "heatwave", "temperature", "burns on contact",
                      "unbearable", "dangerous temperatures"]),
    ("Heritage Damage", ["heritage", "historic", "ancient", "museum"]),
    ("Streetlight", ["streetlight", "street light", "unlit", "flickering", "sparking",
                      "lights out", "wiring theft", "electrical hazard"]),
    ("Noise", ["music", "amplifier", "band playing", "drilling", "idling", "audible"]),
    ("Waste", ["garbage", "bins overflowing", "overflowing", "dumped", "dead animal",
                "trash", "waste"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "buckled", "subsided",
                      "subsidence", "collapsed", "crater", "footpath broken",
                      "footpath tiles broken", "paving", "cobblestones broken",
                      "manhole cover missing", "bench and upturned paving"]),
]

# Severity keywords from README/agents.md enforcement rule 2. Each canonical
# keyword maps to itself plus the grammatical variants seen in real
# complaints (e.g. "hospitalised", "collapsed") so the rule isn't defeated by
# tense/inflection while still only firing on the literal words specified.
SEVERITY_KEYWORDS = {
    "injury": ["injury", "injured"],
    "child": ["child"],
    "school": ["school"],
    "hospital": ["hospital", "hospitalised", "hospitalized"],
    "ambulance": ["ambulance"],
    "fire": ["fire"],
    "hazard": ["hazard"],
    "fell": ["fell"],
    "collapse": ["collapse", "collapsed"],
}


def _find_category_matches(description: str):
    text = description.lower()
    matches = []
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in text:
                matches.append((category, kw))
                break
    return matches


def _find_severity_hit(description: str):
    text = description.lower()
    for variants in SEVERITY_KEYWORDS.values():
        for variant in variants:
            if variant in text:
                return variant
    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description was provided, so category cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    matches = _find_category_matches(description)
    reason_parts = []

    if not matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_parts.append("no recognised category keywords were found in the description")
    else:
        category, matched_word = matches[0]
        distinct_categories = {c for c, _ in matches}
        if len(distinct_categories) > 1:
            flag = "NEEDS_REVIEW"
            other_words = ", ".join(f"'{w}' ({c})" for c, w in matches[1:])
            reason_parts.append(
                f"description mentions '{matched_word}' ({category}) but also {other_words}, "
                f"making the category ambiguous"
            )
        else:
            flag = ""
            reason_parts.append(f"description mentions '{matched_word}'")

    severity_hit = _find_severity_hit(description)
    if severity_hit:
        priority = "Urgent"
        reason_parts.append(f"marked Urgent due to severity keyword '{severity_hit}'")
    else:
        priority = "Standard"

    reason = "; ".join(reason_parts)
    reason = reason[0].upper() + reason[1:] + "."

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

    A row that raises an error during classification is still written out
    (category Other, priority Low, flag NEEDS_REVIEW, error in reason) so one
    bad row never crashes the batch or drops a complaint from the output.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append({
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
