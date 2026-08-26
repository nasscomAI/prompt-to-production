"""
UC-0A — Complaint Classifier
Built with the RICE → agents.md → skills.md → CRAFT workflow.

Enforcement implemented here (mirrors agents.md):
- category: exact strings from the allowed taxonomy only
- priority: Urgent whenever a severity keyword appears in the description
- reason: cites the specific matched words from the description
- flag: NEEDS_REVIEW when zero or 2+ categories match (genuine ambiguity)
- batch never crashes on a bad row and never drops rows
"""
import argparse
import csv
import re
import sys

# Allowed taxonomy — exact output strings (agents.md enforcement rule 1)
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole"],
    "Flooding":        ["flooded", "floods", "flooding", "waterlogged", "standing in water", "knee-deep"],
    "Streetlight":     ["streetlight", "street light", "lights out", "light out", "light not working", "flickering"],
    "Waste":           ["garbage", "waste", "trash", "dumped", "dumping", "bins", "dead animal", "litter"],
    "Noise":           ["noise", "loud music", "music past", "loudspeaker", "playing music"],
    "Road Damage":     ["road surface", "cracked", "sinking", "footpath", "tiles broken", "road caved", "uneven surface"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard":     ["heatwave", "heat wave", "no shade", "scorching", "heat stress"],
    "Drain Blockage":  ["drain blocked", "drain block", "blocked drain", "drainage blocked", "manhole", "sewer", "choked drain"],
}

# Severity keywords that must trigger Urgent (agents.md enforcement rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _find_matches(text: str, keywords: list) -> list:
    """Return the keywords present in text (case-insensitive, stem match)."""
    low = text.lower()
    return [kw for kw in keywords if kw in low]


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
            "priority": "Standard",
            "reason": "No usable description text was provided, so no category evidence exists.",
            "flag": "NEEDS_REVIEW",
        }

    # Score every category by keyword evidence in the description only
    hits = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = _find_matches(description, keywords)
        if matched:
            hits[category] = matched

    severity_matched = _find_matches(description, SEVERITY_KEYWORDS)

    flag = ""
    if not hits:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_evidence = "no taxonomy keyword matched"
    else:
        # Best-scoring category wins; earliest mention breaks ties
        def rank(cat):
            first_pos = min(description.lower().find(kw) for kw in hits[cat])
            return (-len(hits[cat]), first_pos)

        ordered = sorted(hits, key=rank)
        category = ordered[0]
        if len(hits) > 1:
            # Multi-signal description → genuinely ambiguous (enforcement rule 4)
            flag = "NEEDS_REVIEW"
        category_evidence = "matched " + ", ".join(
            "'%s'" % kw for kw in hits[category]
        )

    if severity_matched:
        priority = "Urgent"
        priority_evidence = " and severity words " + ", ".join(
            "'%s'" % kw for kw in severity_matched
        ) + " require Urgent"
    elif category == "Noise":
        priority = "Low"
        priority_evidence = " with no severity words, so nuisance-level Low"
    else:
        priority = "Standard"
        priority_evidence = " with no severity words, so Standard"

    reason = "Description %s%s." % (category_evidence, priority_evidence)

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
    Never crashes on a bad row and never drops rows (enforcement rule 6).
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        sys.exit("Cannot read input file %s: %s" % (input_path, exc))

    results = []
    flagged = 0
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:  # a bad row must not kill the batch
            result = {
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": "Row could not be classified (%s)." % exc,
                "flag": "NEEDS_REVIEW",
            }
        if result["flag"]:
            flagged += 1
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)

    print("Classified %d rows (%d flagged NEEDS_REVIEW)." % (len(results), flagged))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
