"""
UC-0A — Complaint Classifier.
Classifies civic complaints into a fixed 10-category taxonomy, assigns
priority from severity keywords, and flags genuinely ambiguous rows.
Built from uc-0a/agents.md and uc-0a/skills.md (RICE).
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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Phrases are matched case-insensitively against the description (substring).
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "standing in water", "rain"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "lamp"],
    "Waste": ["garbage", "waste", "dead animal", "bins", "litter", "debris"],
    "Noise": ["music", "noise", "noisy", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles broken", "road damaged"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave", "heat wave"],
    "Drain Blockage": ["drain", "manhole", "blocked", "clogged", "sewer"],
}


def _has_severity(text: str):
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(keyword), text):
            return keyword
    return None


def _matched_phrases(text: str, phrases):
    matches = []
    for phrase in phrases:
        if re.search(r"\b" + re.escape(phrase) + r"s?\b", text):
            matches.append(phrase)
    return matches


def classify_complaint(row: dict) -> dict:
    """One complaint row in -> category + priority + reason + flag out."""
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip().lower()

    if not description:
        return _flagged(complaint_id, "Other", "NEEDS_REVIEW",
                        "No description present, cannot classify.")

    scores = {}
    for category, phrases in CATEGORY_KEYWORDS.items():
        matched = _matched_phrases(description, phrases)
        if matched:
            scores[category] = (len(matched), matched)

    if not scores:
        return _flagged(complaint_id, "Other", "NEEDS_REVIEW",
                        "No category keywords found in the description, cannot classify confidently.")

    max_score = max(v[0] for v in scores.values())
    top = [c for c, (s, _) in scores.items() if s == max_score]

    category = top[0]
    flag = "NEEDS_REVIEW" if len(top) > 1 else ""

    cited = ", ".join(f"'{p}'" for p in scores[category][1])
    severity = _has_severity(description)
    priority = "Urgent" if severity else "Standard"

    reason = f"Description cites {cited} which indicates {category}."
    if severity:
        reason += f" Severity keyword '{severity}' present, so priority is Urgent."
    return {"complaint_id": complaint_id, "category": category,
            "priority": priority, "reason": reason, "flag": flag}


def _flagged(complaint_id, category, flag, reason):
    return {"complaint_id": complaint_id, "category": category,
            "priority": "Standard", "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    rows = []
    flagged = 0
    total = 0
    with open(input_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            total += 1
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never drop a row
                result = _flagged(str(row.get("complaint_id", total)), "Other", "NEEDS_REVIEW",
                                  f"Row could not be processed ({exc}).")
            if result["flag"]:
                flagged += 1
            rows.append(result)

    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processed {total} rows. Rows flagged NEEDS_REVIEW: {flagged}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")