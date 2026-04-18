"""
UC-0A — Complaint Classifier
CRAFT-tested implementation guided by agents.md (RICE) and skills.md.
City: Hyderabad

Run:
  python classifier.py --input ../data/city-test-files/test_hyderabad.csv --output results_hyderabad.csv
"""

import argparse
import csv
import re

# ── Taxonomy ──────────────────────────────────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords that MUST trigger Urgent priority (case-insensitive)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire",
    "hazard", "fell", "collapse", "collapsed", "hospitalised",
    "crater", "lives", "life at risk"
]

# ── Classification rules ──────────────────────────────────────────────────────
# Each rule: (regex pattern on description, category)
# Order matters — first match wins.
CATEGORY_RULES = [
    # Flooding
    (r"\bflood(ed|ing|s)?\b|\bunderpass flood|\bwater log", "Flooding"),
    # Drain Blockage
    (r"\bdrain\b.*\bblock(ed)?\b|\bblock(ed)?\b.*\bdrain\b|\bstormwater drain|mosquito breeding", "Drain Blockage"),
    # Pothole
    (r"\bpothole(s)?\b|\bpotholes?\b", "Pothole"),
    # Road Damage
    (r"\broad colla?ps(e|ed)?\b|\bcra?ter\b|\broad.*damage|\bdamage.*road", "Road Damage"),
    # Waste
    (r"\bwaste\b|\bgarbage\b|\bwaste not cleared\b|\boverflow\b", "Waste"),
    # Noise
    (r"\bnoise\b|\bdrilling\b|\bidling\b|\bengines? on\b|\bsound\b", "Noise"),
    # Heritage Damage
    (r"\bheritage\b", "Heritage Damage"),
    # Streetlight
    (r"\bstreetlight(s)?\b|\blight(s)? (not working|off|broken|out)\b", "Streetlight"),
    # Heat Hazard
    (r"\bheat\b|\btemperature\b|\bsun(stroke)?\b", "Heat Hazard"),
]

# Low-priority signal words (when no urgent keyword and category is not critical)
LOW_PRIORITY_SIGNALS = [r"\bslow(ed)?\b", r"\bminor\b", r"\bsmall\b"]


def _has_urgent_keyword(text: str) -> bool:
    text_lower = text.lower()
    for kw in URGENT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
            return True
    return False


def _determine_category(description: str):
    """
    Returns (category, needs_review).
    Matches description against CATEGORY_RULES in order.
    Falls back to Other + NEEDS_REVIEW if no rule matches.
    """
    text_lower = description.lower()
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, text_lower):
            return category, False
    return "Other", True


def _determine_priority(description: str, category: str) -> str:
    if _has_urgent_keyword(description):
        return "Urgent"
    # Flooding + Drain Blockage at minimum Standard; heat/streetlight could be low
    low_category = category in ("Streetlight", "Heat Hazard", "Noise")
    if low_category:
        for pattern in LOW_PRIORITY_SIGNALS:
            if re.search(pattern, description.lower()):
                return "Low"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Construct a one-sentence reason citing words from the description.
    """
    # Find the urgent trigger word if any
    urgent_word = None
    for kw in URGENT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", description.lower()):
            urgent_word = kw
            break

    # Grab a short excerpt from the description (first 80 chars)
    excerpt = description.strip()
    if len(excerpt) > 80:
        excerpt = excerpt[:77] + "..."

    reason = f"Classified as '{category}' based on description: \"{excerpt}\""
    if urgent_word:
        reason += f" — priority set to Urgent due to keyword '{urgent_word}'."
    else:
        reason += f" — priority set to {priority}."
    return reason


# ── Skill: classify_complaint ─────────────────────────────────────────────────
def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Implements agents.md RICE enforcement rules.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, needs_review = _determine_category(description)
    priority = _determine_priority(description, category)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if needs_review else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Skill: batch_classify ─────────────────────────────────────────────────────
def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never aborts on a bad row — logs and continues.
    """
    results = []
    errors = []
    urgent_count = 0
    review_count = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            cid = row.get("complaint_id", "UNKNOWN")
            errors.append((cid, str(exc)))
            result = {
                "complaint_id": cid,
                "category": "Other",
                "priority": "Low",
                "reason": "Classification error — row skipped.",
                "flag": "NEEDS_REVIEW",
            }

        results.append(result)
        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            review_count += 1

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    print(f"\n{'='*55}")
    print(f"  UC-0A Complaint Classifier — Results Summary")
    print(f"{'='*55}")
    print(f"  Total rows processed : {len(rows)}")
    print(f"  Urgent               : {urgent_count}")
    print(f"  NEEDS_REVIEW         : {review_count}")
    print(f"  Classification errors: {len(errors)}")
    if errors:
        for cid, err in errors:
            print(f"    ⚠ {cid}: {err}")
    print(f"  Output written to    : {output_path}")
    print(f"{'='*55}\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
