"""
UC-0A — Complaint Classifier
Deterministic, rule-based triage implementing agents.md enforcement rules
and the skills.md contracts for classify_complaint / batch_classify.
"""
import argparse
import csv
import re
import sys

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

SEVERITY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed",
]

CATEGORY_PATTERNS = [
    ("Pothole", r"\bpotholes?\b"),
    ("Flooding", r"\bflood(?:ed|ing|s)?\b|\bwaterlogg(?:ed|ing)\b|\bwater[- ]logged\b|\brainwater\b"),
    ("Drain Blockage", r"\bdrains?\b|\bdrainage\b|\bdraining\b|\bsewerage?\b|\bclogg(?:ed|ing)\b|\bsewage overflow\b"),
    ("Streetlight", r"\bstreet ?lights?\b|\bstreetlamp\b|\blamp ?posts?\b|\bno lighting\b|\bunlit\b"),
    ("Waste", r"\bgarbage\b|\bwaste\b|\btrash\b|\brubbish\b|\blitter\b|\bdump(ing)?\b|\bdead animal\b|\bcarcass\b"),
    ("Noise", r"\bnoise\b|\bnoisy\b|\bloudspeaker?s?\b|\b(?:loud |amplified |blaring )?music\b|\b(?:wedding |brass )?band\b|\bdrilling\b|\bconstruction noise\b"),
    ("Heritage Damage", r"\bheritage\b|\bmonument\b|\bstatue\b|\bmural\b|\bhistoric (?:building|structure)\b"),
    ("Heat Hazard", r"\bheat ?waves?\b|\bextreme heat\b|\bscorching\b|\btemperatures?\b|\bmelting\b|\bstoring heat\b|\bfull sun\b"),
    ("Road Damage", r"\broad damage\b|\bsinkhole\b|\b(?:road|roads|footpath|pavement|sidewalk|paving|surface)\b[^.;]{0,40}\b(?:cracked|broken|damaged|upturned|sinking|caving|dug|buckled|subsided|collapsed)\b|\b(?:cracked|broken|upturned|sinking) (?:road|roads|footpath|pavement|sidewalk|paving)\b"),
]

COMPILED = {cat: re.compile(pat, re.IGNORECASE) for cat, pat in CATEGORY_PATTERNS}
SEVERITY_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in SEVERITY_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def _find_matches(text):
    found = {}
    for cat, rx in COMPILED.items():
        m = rx.search(text)
        if m:
            found[cat] = m.group(0)
    return found


def _quote(text, phrase):
    idx = text.lower().find(phrase.lower())
    if idx >= 0:
        return text[idx:idx + len(phrase)]
    return phrase


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip() or "<missing>"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty, so no classification evidence exists.",
            "flag": "NEEDS_REVIEW",
        }

    matches = _find_matches(description)

    if not matches:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if SEVERITY_RE.search(description) else "Low",
            "reason": f'Description "{description[:60]}" does not match any known category.',
            "flag": "NEEDS_REVIEW",
        }

    if len(matches) > 1:
        category = list(matches)[0]
        flag = "NEEDS_REVIEW"
        ambiguity = ""
    else:
        category = next(iter(matches))
        flag = ""
        ambiguity = ""

    cited = _quote(description, matches[category])
    reason = f'Description mentions "{cited}", which indicates {category}.'

    sev = SEVERITY_RE.search(description)
    if sev:
        priority = "Urgent"
        reason = f'Description mentions "{_quote(description, sev.group(0))}" and "{cited}", so this is urgent {category}.'
    elif category == "Noise":
        priority = "Low"
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig", errors="replace") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    flagged = 0

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(rows, start=1):
            try:
                result = classify_complaint(row)
                assert result["category"] in CATEGORIES, "invalid category"
                assert result["priority"] in ("Urgent", "Standard", "Low"), "invalid priority"
                assert result["reason"].strip(), "empty reason"
            except Exception as exc:
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip() or "<missing>",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row {i} failed classification ({exc}).",
                    "flag": "NEEDS_REVIEW",
                }
            if result["flag"] == "NEEDS_REVIEW":
                flagged += 1
            writer.writerow(result)

    print(f"Rows read: {len(rows)} | classified: {len(rows)} | flagged NEEDS_REVIEW: {flagged}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    print(f"Done. Results written to {args.output}")
