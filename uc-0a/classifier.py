"""
UC-0A — Complaint Classifier
Implemented from uc-0a/README.md, uc-0a/agents.md, and uc-0a/skills.md.

RICE enforcement reflected here:
- Exact taxonomy: 10 allowed categories, 3 allowed priorities.
- Severity keywords (case-insensitive) force priority Urgent.
- One-sentence reason citing the specific triggering words from the description.
- Genuinely ambiguous or unclassifiable complaints -> category Other, flag NEEDS_REVIEW.
- Batch run never crashes on a bad row and always writes an output file.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}
ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = (
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
)
BLOCKAGE_KEYWORDS = ("block", "clog", "chok", "overflow")

OTHER = "Other"
NEEDS_REVIEW = "NEEDS_REVIEW"
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _match(text, keywords):
    """Case-insensitive prefix match. Returns the first matching keyword or None."""
    if not text:
        return None
    lowered = text.lower()
    for keyword in keywords:
        if re.search(r"\b" + re.escape(keyword), lowered):
            return keyword
    return None


def _detect_signals(description):
    """Classify which allowed categories the description points to."""
    return {
        "pothole": _match(description, ("pothole",)),
        "road": _match(description, (
            "road surface", "crack", "sink", "broken", "upturned",
            "footpath", "tiles", "manhole", "deteriorat",
        )),
        "flood": _match(description, (
            "flood", "waterlog", "submerged", "knee-deep", "ankle-deep",
            "stagnant", "standing water",
        )),
        "drain": _match(description, ("drain", "sewage")),
        "street": _match(description, (
            "streetlight", "street light", "light", "lamp", "flicker", "spark",
        )),
        "waste": _match(description, (
            "garbage", "waste", "rubbish", "litter", "trash", "debris",
            "carcass", "dead animal", "dumped",
        )),
        "noise": _match(description, (
            "noise", "music", "loud", "amplif", "speaker", "band",
        )),
        "heritage": _match(description, ("heritage", "monument")),
        "heat": _match(description, ("heat",)),
    }


def _categorize(description, signals):
    """Return (category, flag, cat_word, extra_word, kind)."""
    if signals["heritage"] and signals["street"]:
        return OTHER, NEEDS_REVIEW, signals["heritage"], signals["street"], "conflicting_signals"
    if signals["flood"] and signals["drain"]:
        return OTHER, NEEDS_REVIEW, signals["flood"], signals["drain"], "conflicting_signals"
    if signals["noise"]:
        return "Noise", "", signals["noise"], None, "category"
    if signals["drain"] and _match(description, BLOCKAGE_KEYWORDS):
        return "Drain Blockage", "", signals["drain"], None, "category"
    order = [
        ("pothole", "Pothole"),
        ("flood", "Flooding"),
        ("street", "Streetlight"),
        ("waste", "Waste"),
        ("noise", "Noise"),
        ("heritage", "Heritage Damage"),
        ("road", "Road Damage"),
        ("drain", "Drain Blockage"),
        ("heat", "Heat Hazard"),
    ]
    for key, name in order:
        if signals[key]:
            return name, "", signals[key], None, "category"
    return OTHER, NEEDS_REVIEW, None, None, "no_signal"


def _priority(description):
    severity = _match(description, SEVERITY_KEYWORDS)
    if severity:
        return "Urgent"
    return "Standard"


def _normal_reason(description, category, cat_word):
    if _match(description, SEVERITY_KEYWORDS):
        kw = _match(description, SEVERITY_KEYWORDS)
        return (
            f"Category is {category} because '{cat_word}' appears in the description, "
            f"and priority is Urgent because '{kw}' also appears in the description."
        )
    return (
        f"Category is {category} because '{cat_word}' appears in the description, "
        "and priority is Standard because no Urgent-trigger word appears in the description."
    )


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag.
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")
    priority = _priority(description)

    if not description:
        category = OTHER
        flag = NEEDS_REVIEW
        reason = (
            f"Category is {category} because the description is missing or empty, "
            f"and the complaint is flagged {NEEDS_REVIEW}."
        )
    else:
        category, flag, cat_word, extra_word, kind = _categorize(description, _detect_signals(description))
        if kind == "conflicting_signals":
            if priority == "Urgent":
                kw = _match(description, SEVERITY_KEYWORDS)
                reason = (
                    f"Category is Other because '{cat_word}' and '{extra_word}' both "
                    f"appear in the description, making the category genuinely ambiguous, "
                    f"and priority is Urgent because '{kw}' also appears in the description."
                )
            else:
                reason = (
                    f"Category is Other because '{cat_word}' and '{extra_word}' both "
                    f"appear in the description, making the category genuinely ambiguous."
                )
        elif kind == "no_signal":
            if priority == "Urgent":
                kw = _match(description, SEVERITY_KEYWORDS)
                reason = (
                    f"Category is Other because the description does not clearly indicate "
                    f"any allowed category, the complaint is flagged {NEEDS_REVIEW}, "
                    f"and priority is Urgent because '{kw}' appears in the description."
                )
            else:
                reason = (
                    f"Category is Other because the description does not clearly indicate "
                    f"any allowed category, and the complaint is flagged {NEEDS_REVIEW}."
                )
        else:
            reason = _normal_reason(description, category, cat_word)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _fallback_result(row, index):
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    return {
        "complaint_id": complaint_id,
        "category": OTHER,
        "priority": "Standard",
        "reason": f"Row {index} could not be classified and is flagged {NEEDS_REVIEW}.",
        "flag": NEEDS_REVIEW,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row and always produces an output file.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as infile, \
            open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception:
                result = _fallback_result(row, index)
            try:
                writer.writerow(result)
            except Exception:
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")