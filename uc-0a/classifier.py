"""
UC-0A — Complaint Classifier
Rule-based classifier implementing the RICE enforcement rules from agents.md.
Categories are restricted to the 10 allowed strings; Urgent is triggered only by
the 9 severity keywords; ambiguous rows are flagged NEEDS_REVIEW, never guessed.
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
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword families: schema-priority order (checked first wins ties).
# weight 2 = strong primary noun, weight 1 = supporting/contextual signal.
CATEGORY_KEYWORDS = {
    "Pothole": [("pothole", 2), ("crater", 2), ("potholes", 2)],
    "Flooding": [
        ("flood", 2), ("waterlogging", 2), ("flooded", 2),
        ("rainwater", 1), ("draining", 1), ("overflowing drain", 1),
    ],
    "Streetlight": [
        ("streetlight", 2), ("street light", 2), ("lamp post", 1),
        ("darkness", 2), ("substation", 1), ("light not", 1), ("bulb", 1),
    ],
    "Waste": [
        ("waste", 2), ("garbage", 2), ("trash", 2), ("rubbish", 2),
        ("dumping", 1), ("overflowing bins", 2), ("refuse", 1),
    ],
    "Noise": [
        ("noise", 2), ("loudspeaker", 2), ("loudspeakers", 2),
        ("amplifier", 2), ("amplifiers", 2), ("band playing", 2),
        ("music", 1),
    ],
    "Road Damage": [
        ("road surface", 2), ("buckled", 2), ("subsided", 2),
        ("footpath", 2), ("sinking", 1), ("broken road", 2),
        ("paving", 1), ("surface cracked", 1),
    ],
    "Heritage Damage": [
        ("heritage", 2), ("historic", 2), ("cobblestone", 2),
        ("monument", 2), ("memorial", 2), ("defaced", 2),
        ("heritage stone", 2), ("museum", 1), ("tram", 1),
    ],
    "Heat Hazard": [
        ("heat wave", 2), ("heatwave", 2), ("heat", 2),
        ("scorching", 1), ("dehydration", 1), ("water shortage in summer", 1),
    ],
    "Drain Blockage": [
        ("drain blocked", 2), ("blocked drain", 2), ("sewer", 2),
        ("drainage clogged", 2), ("clogged", 1), ("gutter", 1),
    ],
}


def _contains(text: str, keyword: str) -> bool:
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()
    text = description.lower()

    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty — no classifiable signal present, routed for manual review.",
            "flag": "NEEDS_REVIEW",
        }

    # --- Category: score every family, schema order breaks ties ---
    scores = {}
    matched_words = {}
    for family in ALLOWED_CATEGORIES:
        keywords = CATEGORY_KEYWORDS.get(family, [])
        score = 0
        hits = []
        for keyword, weight in keywords:
            if _contains(text, keyword):
                score += weight
                hits.append(keyword)
        if score > 0:
            scores[family] = score
            matched_words[family] = hits

    # Locational qualifier: "heritage/historic precinct|zone|area" describes
    # WHERE the complaint is, not damage TO heritage — downweight that family.
    if re.search(r"\b(heritage|historic) (precinct|zone|area|quarter)\b", text):
        if "Heritage Damage" in scores and scores["Heritage Damage"] > 1:
            scores["Heritage Damage"] = 1

    if not scores:
        category, flag = "Other", "NEEDS_REVIEW"
        reason = (
            f"No keyword from any allowed category family appears in the "
            f"description ('{description[:60]}...'), so it is filed as Other."
        )
    else:
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_family, top_score = ranked[0]
        category = top_family
        if len(ranked) > 1 and ranked[1][1] == top_score:
            # Genuine ambiguity: equal evidence for two families.
            flag = "NEEDS_REVIEW"
            reason = (
                f"Description matches '{ranked[0][0]}' and '{ranked[1][0]}' with "
                f"equal strength (keywords: {', '.join(matched_words[ranked[0][0]])} / "
                f"{', '.join(matched_words[ranked[1][0]])}) — flagged instead of guessed."
            )
        else:
            flag = ""
            reason = (
                f"Classified as {category} because the description cites "
                f"{', '.join(matched_words[top_family])}."
            )

    # --- Priority: severity keywords only, per RICE enforcement rule 2 ---
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if _contains(text, kw)]
    if severity_hits:
        priority = "Urgent"
        reason += f" Priority Urgent: severity keyword(s) '{', '.join(severity_hits)}' present."
    else:
        priority = "Standard"

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
    Never crashes on bad rows: unparseable rows are emitted as Other/NEEDS_REVIEW.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_read = urgent = flagged = failures = 0

    try:
        infile = open(input_path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print(f"ERROR: cannot read input file {input_path}: {exc}", file=sys.stderr)
        raise SystemExit(1)

    with infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            rows_read += 1
            try:
                result = classify_complaint(row)
            except Exception as exc:  # defensive: one bad row must not kill the batch
                result = {
                    "complaint_id": (row.get("complaint_id") or "UNKNOWN").strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row could not be parsed ({exc}) — routed for manual review.",
                    "flag": "NEEDS_REVIEW",
                }
                failures += 1
            if result["priority"] == "Urgent":
                urgent += 1
            if result["flag"] == "NEEDS_REVIEW":
                flagged += 1
            writer.writerow(result)

    print(
        f"Batch complete: {rows_read} rows read, {urgent} Urgent, "
        f"{flagged} flagged NEEDS_REVIEW, {failures} parse failures."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
