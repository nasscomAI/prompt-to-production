"""UC-0A complaint classifier."""
import argparse
import csv
import re

ALLOWED_CATEGORIES = (
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
)
URGENT_TERMS = (
    "injury", "child", "school", "hospital", "ambulance", "fire",
    "hazard", "fell", "collapse",
)


def _contains_any(text, terms):
    return any(re.search(r"\b{}\b".format(re.escape(term)), text) for term in terms)


def _category_for(description):
    text = description.lower()
    matches = []
    rules = (
        ("Pothole", ("pothole",)),
        ("Flooding", ("flood", "flooding", "waterlogging")),
        ("Streetlight", ("streetlight", "street light", "lamp post", "lamp")),
        ("Waste", ("waste", "garbage", "litter", "rubbish", "dump")),
        ("Noise", ("noise", "loudspeaker", "loud music", "sound pollution")),
        ("Road Damage", ("road damage", "road surface", "tarmac", "asphalt", "crack")),
        ("Heritage Damage", ("heritage", "monument", "historic", "historical")),
        ("Heat Hazard", ("heatwave", "heat wave", "hot surface", "temperature", "°c")),
        ("Drain Blockage", ("drain", "blocked", "clogged", "sewer")),
    )
    for category, terms in rules:
        if any(term in text for term in terms):
            matches.append(category)
    if len(matches) == 1:
        return matches[0], ""
    return "Other", "NEEDS_REVIEW"

def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided.",
            "flag": "NEEDS_REVIEW",
        }
    category, flag = _category_for(description)
    priority = "Urgent" if _contains_any(description.lower(), URGENT_TERMS) else "Standard"
    if flag:
        reason = "Description is ambiguous and does not identify one allowed category."
    else:
        reason = "Classified as {} based on: {}.".format(category, description.rstrip("."))
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, "r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or "complaint_id" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a complaint_id column")
        if "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a description column")
        rows = [classify_complaint(row) for row in reader]
    with open(output_path, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
