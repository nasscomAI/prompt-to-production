"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify using keyword-based
enforcement rules defined in agents.md and skills.md.
"""
import argparse
import csv
import re
import sys

# ── Taxonomy ──────────────────────────────────────────────────────────────────
CATEGORIES = [
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

# Keywords for each category (case-insensitive, matched against description)
CATEGORY_KEYWORDS = {
    "Pothole":        ["pothole", "pot-hole", "pot hole"],
    "Flooding":       ["flood", "flooded", "flooding", "waterlogged", "waterlog",
                       "submerged", "inundated", "knee-deep", "standing water"],
    "Streetlight":    ["streetlight", "street light", "lamp", "lighting", "lights out",
                       "light out", "dark", "flickering", "sparking"],
    "Waste":          ["garbage", "waste", "trash", "rubbish", "litter", "overflowing bin",
                       "bin", "dump", "dumped", "dumping", "dead animal", "carcass"],
    "Noise":          ["noise", "loud", "music", "sound", "disturbance", "honking",
                       "nuisance", "midnight"],
    "Road Damage":    ["road", "crack", "cracked", "sinking", "surface", "footpath",
                       "pavement", "tiles", "broken", "upturned", "manhole", "utility work"],
    "Heritage Damage":["heritage", "historical", "monument", "old city", "rasta peth",
                       "ancient"],
    "Heat Hazard":    ["heat", "temperature", "hot", "sun", "heatwave"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "sewer", "gutter"],
}

# Severity keywords that trigger Urgent (from agents.md enforcement)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _find_severity(description: str) -> str | None:
    """Return the first severity keyword found in description, or None."""
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            return kw
    return None


def _find_category(description: str) -> tuple[str, str | None]:
    """
    Return (category, matched_keyword).
    Scores each category by count of keyword hits; picks highest.
    Returns ("Other", None) if no keywords match.
    """
    desc_lower = description.lower()
    scores: dict[str, tuple[int, str]] = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in scores:
                    scores[cat] = (0, kw)
                count, first_kw = scores[cat]
                scores[cat] = (count + 1, first_kw)

    if not scores:
        return "Other", None

    best_cat = max(scores, key=lambda c: scores[c][0])
    return best_cat, scores[best_cat][1]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine category
    category, matched_kw = _find_category(description)

    # Determine priority — severity keywords always trigger Urgent
    severity_hit = _find_severity(description)
    if severity_hit:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Build reason citing specific description words
    if severity_hit and matched_kw:
        reason = (
            f"Description contains severity keyword '{severity_hit}' and "
            f"matches category '{category}' via keyword '{matched_kw}'."
        )
    elif severity_hit:
        reason = (
            f"Description contains severity keyword '{severity_hit}'; "
            f"category set to '{category}' as best match."
        )
    elif matched_kw:
        reason = f"Description contains '{matched_kw}', indicating {category}."
    else:
        reason = "No specific category keywords found in description."

    # Set flag if category is genuinely ambiguous
    flag = "NEEDS_REVIEW" if category == "Other" else ""

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
    Does not crash on bad rows — logs errors to stderr.
    """
    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                print(f"ERROR classifying {row.get('complaint_id', '?')}: {e}", file=sys.stderr)
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification error.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
