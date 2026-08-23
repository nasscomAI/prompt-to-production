"""UC-0A — Complaint Classifier."""

import argparse
import csv
import re

CATEGORIES = (
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
)

URGENT_TERMS = ("injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse")

CATEGORY_PATTERNS = (
    ("Drain Blockage", ("drain blocked", "blocked drain", "drain blockage", "drain is blocked")),
    ("Flooding", ("flood", "flooded", "flooding", "waterlogged", "water logged", "standing water", "inundated")),
    ("Streetlight", ("streetlight", "street light", "lamp post", "street lamp")),
    ("Pothole", ("pothole", "pot hole")),
    ("Waste", ("garbage", "waste", "rubbish", "litter", "dumped")),
    ("Noise", ("noise", "loud music", "loudspeaker", "sound")),
    ("Heritage Damage", ("heritage", "historic building", "monument", "heritage site")),
    ("Heat Hazard", ("heat", "extreme heat", "heatwave", "hot surface")),
    ("Road Damage", ("road damage", "road surface", "cracked road", "sinking road", "damaged road")),
)


def _find_category(description: str) -> tuple[str, bool, str]:
    text = description.lower()
    matches = [(category, phrase) for category, patterns in CATEGORY_PATTERNS for phrase in patterns if phrase in text]
    categories = {category for category, _ in matches}
    if len(categories) == 1:
        category = next(iter(categories))
        phrase = next(phrase for cat, phrase in matches if cat == category)
        return category, False, phrase
    return "Other", True, "ambiguous complaint" if matches else "no supported category evidence"


def _find_priority(description: str) -> tuple[str, str]:
    text = description.lower()
    for term in URGENT_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", text):
            return "Urgent", term
    return "Standard", "no urgent severity keyword"


def classify_complaint(row: dict) -> dict:
    """Classify one complaint using only the supplied row."""
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    if not description:
        return {"complaint_id": complaint_id, "category": "Other", "priority": "Low", "reason": "Description is missing.", "flag": "NEEDS_REVIEW"}

    category, ambiguous, category_evidence = _find_category(description)
    priority, priority_evidence = _find_priority(description)
    flag = "NEEDS_REVIEW" if ambiguous else ""
    if ambiguous:
        reason = f'Category could not be determined confidently from the description; evidence: "{category_evidence}".'
    elif priority == "Urgent":
        reason = f'Classified as {category}; priority is Urgent because the description contains "{priority_evidence}".'
    else:
        reason = f'Classified as {category}; no required urgent severity keyword was found.'
    return {"complaint_id": complaint_id, "category": category, "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str) -> None:
    """Classify every CSV row and keep processing if one row is malformed."""
    fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, newline="", encoding="utf-8") as input_file, open(output_path, "w", newline="", encoding="utf-8") as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {"complaint_id": str(row.get("complaint_id", "")).strip(), "category": "Other", "priority": "Low", "reason": f"Classification failed safely: {exc}.", "flag": "NEEDS_REVIEW"}
            writer.writerow(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to results_[city].csv")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
