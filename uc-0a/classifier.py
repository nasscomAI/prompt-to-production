"""
UC-0A — Complaint Classifier
Enforcement rules (from agents.md / skills.md):
- Category is exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
  Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
- Priority is Urgent if any severity keyword appears: injury, child, school,
  hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard,
  unless the complaint is clearly trivial, then Low.
- Every row must include a reason citing specific words from the description.
- If category is genuinely ambiguous, output category: Other and flag: NEEDS_REVIEW.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _has_severity(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in SEVERITY_KEYWORDS)


def _keyword(text: str, *words: str) -> str | None:
    lowered = text.lower()
    for w in words:
        if w in lowered:
            return w
    return None


def _raw_candidate(desc: str) -> str | None:
    lowered = desc.lower()
    mapping = [
        ("pothole", "Pothole"),
        ("flood", "Flooding"),
        ("flooded", "Flooding"),
        ("waterlogging", "Flooding"),
        ("streetlight", "Streetlight"),
        ("street light", "Streetlight"),
        ("light out", "Streetlight"),
        ("lamp", "Streetlight"),
        ("unlit", "Streetlight"),
        ("substation tripped", "Streetlight"),
        ("wiring theft", "Streetlight"),
        ("darkness", "Streetlight"),
        ("lights out", "Streetlight"),
        ("garbage", "Waste"),
        ("waste", "Waste"),
        ("trash", "Waste"),
        ("rubbish", "Waste"),
        ("litter", "Waste"),
        ("bin", "Waste"),
        ("noise", "Noise"),
        ("loud", "Noise"),
        ("music", "Noise"),
        ("band", "Noise"),
        ("road damage", "Road Damage"),
        ("road surface broken", "Road Damage"),
        ("cracked road", "Road Damage"),
        ("broken road", "Road Damage"),
        ("road surface", "Road Damage"),
        ("surface cracked", "Road Damage"),
        ("footpath", "Road Damage"),
        ("pavement", "Road Damage"),
        ("tiles broken", "Road Damage"),
        ("upturned", "Road Damage"),
        ("road subsided", "Road Damage"),
        ("surface melting", "Heat Hazard"),
        ("melting", "Heat Hazard"),
        ("temperature", "Heat Hazard"),
        ("unbearable", "Heat Hazard"),
        ("full sun", "Heat Hazard"),
        ("heritage", "Heritage Damage"),
        ("monument", "Heritage Damage"),
        ("heritage building", "Heritage Damage"),
        ("historic", "Heritage Damage"),
        ("cobblestones", "Heritage Damage"),
        ("heat", "Heat Hazard"),
        ("drain", "Drain Blockage"),
        ("sewer", "Drain Blockage"),
        ("manhole", "Drain Blockage"),
    ]
    for token, cat in mapping:
        if token in lowered:
            return cat
    return None


def _pick_reason(desc: str, category: str) -> str:
    lowered = desc.lower()
    if _has_severity(desc):
        for kw in SEVERITY_KEYWORDS:
            if kw in lowered:
                return f"\"{kw}\" present in description, requiring Urgent priority"
    return f"Description mentions \"{_raw_candidate(desc) or 'the complaint'}\", matching category \"{category}\""


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty; category cannot be determined",
            "flag": "NEEDS_REVIEW",
        }

    category = _raw_candidate(description)

    if _has_severity(description):
        priority = "Urgent"
    elif any(t in description.lower() for t in ("minor", "small", "slight", "very little")):
        priority = "Low"
    else:
        priority = "Standard"

    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    reason = _pick_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(classify_complaint(row))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
