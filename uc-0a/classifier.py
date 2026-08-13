"""
UC-0A — Complaint Classifier
Classifies each complaint row into the official taxonomy with priority, reason, and flag.
Enforcement rules defined in agents.md (derived from README.md).
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire",
    "hazard", "fell", "collapse",
]
MINOR_KEYWORDS = ["cosmetic", "minor", "aesthetic"]

HERITAGE_CONTEXT = ("heritage", "historic", "ancient")
HERITAGE_DAMAGE = ("knocked over", "defaced", "cobblestones", "not replaced", "damaged", "removed", "broken")

CATEGORY_RULES = (
    ("Flooding", ("flooded", "floods", "flood ")),
    ("Pothole", ("pothole",)),
    ("Heat Hazard", ("heatwave", "temperature", "melting", "burn", "°c", "full sun", "heat")),
    ("Drain Blockage", ("drain blocked", "blocked drain", "drain 100% blocked", "drain fully blocked")),
    ("Streetlight", ("streetlight", "street light", "lights out", "unlit", "darkness", "dark at night", "substation", "flickering", "sparking")),
    ("Waste", ("garbage", "dead animal", "bins", "waste", "litter", "trash")),
    ("Noise", ("music", "noise", "drilling", "idling", "amplifier", "wedding band", "speaker")),
    ("Road Damage", ("cracked", "sinking", "subsidence", "subsided", "buckled", "collapsed", "crater", "upturned paving", "footpath", "road surface")),
    ("Heritage Damage", ()),
)


def _sentence_around(text, evidence):
    idx = text.lower().find(evidence.lower())
    if idx == -1:
        idx = 0
    start = max(text.rfind(delim, 0, idx) for delim in ".!?;") + 1
    end = len(text)
    for delim in ".!?;":
        pos = text.find(delim, idx)
        if pos != -1:
            end = min(end, pos + 1)
    return text[start:end].strip()


def _determine_category(description):
    low = description.lower()
    for category, patterns in CATEGORY_RULES:
        if category == "Heritage Damage":
            if any(word in low for word in HERITAGE_CONTEXT) and any(word in low for word in HERITAGE_DAMAGE):
                evidence = next((word for word in HERITAGE_DAMAGE if word in low), "heritage")
                return category, evidence
            continue
        for pattern in patterns:
            if pattern in low:
                return category, pattern
    return "Other", None


def _determine_priority(description):
    low = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in low:
            return "Urgent"
    for keyword in MINOR_KEYWORDS:
        if keyword in low:
            return "Low"
    return "Standard"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id") or "").strip()
    description = str(row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Cannot classify: description is empty or missing.",
            "flag": "NEEDS_REVIEW",
        }

    category, evidence = _determine_category(description)
    priority = _determine_priority(description)

    if category == "Other":
        flag = "NEEDS_REVIEW"
        sentence = _sentence_around(description, description[:12])
        reason = f'Category could not be determined from description alone: "{sentence}" does not clearly match a taxonomy category.'
    else:
        flag = ""
        sentence = _sentence_around(description, evidence)
        reason = f'Classified as {category}: description states "{sentence}".'

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
    Never crashes on bad rows; flagged rows still produce output.
    """
    results = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": str(row.get("complaint_id") or ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row {index} could not be classified: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
