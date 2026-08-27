"""
UC-0A — Complaint Classifier
Rule-based classifier built against the enforcement rules in agents.md.
"""
import argparse
import csv
import re

CAT_POTHOLE = "Pothole"
CAT_FLOODING = "Flooding"
CAT_STREETLIGHT = "Streetlight"
CAT_WASTE = "Waste"
CAT_NOISE = "Noise"
CAT_ROAD_DAMAGE = "Road Damage"
CAT_HERITAGE_DAMAGE = "Heritage Damage"
CAT_HEAT_HAZARD = "Heat Hazard"
CAT_DRAIN_BLOCKAGE = "Drain Blockage"
CAT_OTHER = "Other"

CATEGORIES = [
    CAT_POTHOLE, CAT_FLOODING, CAT_STREETLIGHT, CAT_WASTE, CAT_NOISE,
    CAT_ROAD_DAMAGE, CAT_HERITAGE_DAMAGE, CAT_HEAT_HAZARD, CAT_DRAIN_BLOCKAGE, CAT_OTHER,
]

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed",
]

# Ordered (most specific first) keyword groups per category.
# Order matters: earlier categories win when a description matches more
# than one group, except where an explicit ambiguity check overrides it.
CATEGORY_KEYWORDS = [
    (CAT_POTHOLE, ["pothole"]),
    (CAT_HERITAGE_DAMAGE, ["heritage"]),
    (CAT_HEAT_HAZARD, ["heatwave", "heat wave", "sunstroke", "extreme heat"]),
    (CAT_DRAIN_BLOCKAGE, ["drain block", "drain blocked", "clogged drain", "blocked drain"]),
    (CAT_FLOODING, ["flood", "flooded", "waterlog", "water-log", "inundat"]),
    (CAT_STREETLIGHT, ["streetlight", "street light", "lights out", "light out",
                        "flicker", "spark"]),
    (CAT_WASTE, ["garbage", "waste", "dumped", "dead animal", "trash", "bins", "bin"]),
    (CAT_NOISE, ["noise", "music", "loud"]),
    (CAT_ROAD_DAMAGE, ["footpath", "manhole", "pavement", "road surface",
                        "cracked", "sinking", "road damage"]),
]

# Category pairs that legitimately overlap in this dataset — when keywords
# from both fire on the same description, the row is genuinely ambiguous
# rather than confidently one or the other.
AMBIGUOUS_PAIRS = [
    ({CAT_FLOODING}, {CAT_DRAIN_BLOCKAGE}),
    ({CAT_HERITAGE_DAMAGE}, {CAT_STREETLIGHT}),
]


def _keyword_hit(text: str, keyword: str) -> bool:
    if " " in keyword or "-" in keyword:
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}", text) is not None


def _matched_categories(text: str):
    matches = []
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if _keyword_hit(text, kw):
                matches.append((category, kw))
                break
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    text = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id or "UNKNOWN",
            "category": CAT_OTHER,
            "priority": "Low",
            "reason": "No description provided; cannot determine category from empty input.",
            "flag": "NEEDS_REVIEW",
        }

    matches = _matched_categories(text)

    if not matches:
        category = CAT_OTHER
        flag = "NEEDS_REVIEW"
        reason = "No known category keywords found in description; classified as Other pending manual review."
        matched_words = []
    else:
        matched_cats = {c for c, _ in matches}
        is_ambiguous = any(
            group_a & matched_cats and group_b & matched_cats
            for group_a, group_b in AMBIGUOUS_PAIRS
        )
        category, matched_kw = matches[0]
        matched_words = [kw for _, kw in matches]
        if is_ambiguous:
            flag = "NEEDS_REVIEW"
            other_cats = ", ".join(sorted(matched_cats - {category}))
            reason = (
                f"Description matches both '{category}' (\"{matched_kw}\") "
                f"and {other_cats} keywords — category is genuinely ambiguous."
            )
        else:
            flag = ""
            reason = f"Classified as {category} based on keyword(s): {', '.join(matched_words)}."

    severity_hits = [kw for kw in SEVERITY_KEYWORDS if _keyword_hit(text, kw)]
    if severity_hits:
        priority = "Urgent"
        reason += f" Marked Urgent due to severity keyword(s): {', '.join(severity_hits)}."
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id or "UNKNOWN",
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row — bad rows are flagged NEEDS_REVIEW instead.
    """
    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        input_fieldnames = reader.fieldnames or []
        rows = list(reader)

    output_fieldnames = input_fieldnames + ["category", "priority", "reason", "flag"]
    results = []

    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception as exc:  # never let one bad row kill the batch
            classification = {
                "complaint_id": (row.get("complaint_id") or "UNKNOWN"),
                "category": CAT_OTHER,
                "priority": "Low",
                "reason": f"Row failed to classify due to an unexpected error ({exc}); flagged for manual review.",
                "flag": "NEEDS_REVIEW",
            }
        merged = dict(row)
        merged.update(classification)
        results.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
