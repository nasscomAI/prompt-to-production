"""
UC-0A classifier.py — Municipal complaint classifier (no-API, keyword scoring)
Implements classify_complaint + batch_classify skills from skills.md.
Enforcement from agents.md: exact category strings, severity-keyword Urgent rule,
reason cites description words, NEEDS_REVIEW on ambiguity.
Run: python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import sys
from pathlib import Path

# ── Schema ────────────────────────────────────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST trigger Urgent regardless of category (agents.md enforcement).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword map: category → list of trigger phrases (checked against lowercased description).
# More specific phrases are listed first; order within a category does not affect scoring.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Pothole":        ["pothole", "pot hole", "pot-hole"],
    "Flooding":       ["flood", "flooded", "flooding", "waterlogged", "submerged",
                       "knee-deep", "inundated", "knee deep"],
    "Streetlight":    ["streetlight", "street light", "street-light", "lights out",
                       "light out", "lamp post", "sparking", "flickering"],
    "Waste":          ["garbage", "waste", "bin", "bins", "rubbish", "trash",
                       "litter", "dumped", "dead animal", "animal not removed"],
    "Noise":          ["noise", "music", "loud", "midnight", "sound", "nighttime"],
    "Road Damage":    ["road surface", "manhole", "cracked", "sinking",
                       "road damage", "footpath", "tiles broken", "upturned"],
    "Heritage Damage": ["heritage", "historical", "monument", "ancient"],
    "Heat Hazard":    ["heat", "temperature", "hot"],
    "Drain Blockage": ["drain blocked", "drain blockage", "blocked drain",
                       "drain block", "drainage blocked", "drain"],
    "Other":          [],
}

# Ambiguity threshold: if the runner-up score >= this fraction of top score, flag review.
AMBIGUITY_RATIO = 0.75


# ── Skill: classify_complaint ─────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict: complaint_id, category, priority, reason, flag.
    Never raises — always returns a result.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Score each category by counting distinct keyword hits.
    scores: dict[str, int] = {}
    matched_keywords: dict[str, list[str]] = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        scores[cat] = len(hits)
        matched_keywords[cat] = hits

    # Remove "Other" from scoring — it is the fallback only.
    scores.pop("Other", None)

    top_score = max(scores.values()) if scores else 0

    if top_score == 0:
        category = "Other"
        flag = ""
        reason_cat = "No category keywords matched in description."
    else:
        ranked = sorted(
            [(s, c) for c, s in scores.items() if s > 0],
            reverse=True,
        )
        top_cat = ranked[0][1]
        category = top_cat
        flag = ""

        # Check for ambiguity: runner-up from a different category at >= AMBIGUITY_RATIO.
        if len(ranked) >= 2 and ranked[1][0] / top_score >= AMBIGUITY_RATIO:
            flag = "NEEDS_REVIEW"
            runner_up = ranked[1][1]
            reason_cat = (
                f"Ambiguous between '{top_cat}' "
                f"(keywords: {matched_keywords[top_cat]}) and '{runner_up}' "
                f"(keywords: {matched_keywords[runner_up]})."
            )
        else:
            kws = matched_keywords[top_cat]
            reason_cat = f"Classified as '{top_cat}' based on: {kws}."

    # Priority: Urgent if any severity keyword present — hard rule from agents.md.
    triggered = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if triggered:
        priority = "Urgent"
        reason_priority = f"Urgent: severity keyword(s) found: {triggered}."
    else:
        priority = "Standard"
        reason_priority = ""

    reason = " ".join(filter(None, [reason_cat, reason_priority]))

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Skill: batch_classify ─────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    Processes all rows — row-level errors written to reason field, never abort.
    """
    in_path = Path(input_path).resolve()
    if not in_path.exists():
        sys.exit(f"ERROR [batch_classify]: Input file not found: {in_path}")

    try:
        with in_path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError as e:
        sys.exit(f"ERROR [batch_classify]: Could not read {in_path}: {e}")

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Row-level error during classification: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A: Municipal complaint classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
