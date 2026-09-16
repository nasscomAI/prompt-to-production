import argparse
import csv
import re

CATEGORIES = ("Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other")
URGENT_KEYWORDS = ("injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse")
CATEGORY_RULES = (
    ("Heritage Damage", ("heritage", "monument", "historic", "fort")),
    ("Heat Hazard", ("heatwave", "heat wave", "extreme heat", "heat hazard")),
    ("Drain Blockage", ("drain blocked", "blocked drain", "drain blockage", "clogged drain", "choked drain")),
    ("Streetlight", ("streetlight", "street light", "lamp post", "lighting")),
    ("Pothole", ("pothole", "pot hole")),
    ("Road Damage", ("road damage", "damaged road", "cracked road", "broken road", "road crack", "sinkhole")),
    ("Flooding", ("flood", "flooded", "flooding", "waterlogged", "water logging")),
    ("Waste", ("waste", "garbage", "rubbish", "litter", "dump", "trash")),
    ("Noise", ("noise", "loud", "loudspeaker", "disturbance", "sound pollution")),
)

def _contains(text, keyword):
    return keyword in text if " " in keyword else bool(re.search(r"\b" + re.escape(keyword) + r"\b", text))

def classify_complaint(row: dict) -> dict:
    """Classify one complaint row using the fixed UC-0A schema."""
    complaint_id = row.get("complaint_id", "")
    description = "" if row.get("description") is None else str(row.get("description")).strip()
    text = description.lower()
    if not description:
        return {"complaint_id": complaint_id, "category": "Other", "priority": "Standard", "reason": "The description is missing, so the complaint cannot be categorized.", "flag": "NEEDS_REVIEW"}
    category, evidence = "Other", ""
    for candidate, keywords in CATEGORY_RULES:
        evidence = next((key for key in keywords if _contains(text, key)), "")
        if evidence:
            category = candidate
            break
    urgent = next((key for key in URGENT_KEYWORDS if _contains(text, key)), "")
    priority = "Urgent" if urgent else "Standard"
    if category == "Other":
        reason = "The description does not identify a supported complaint category."
    elif urgent:
        reason = f'The description mentions "{evidence}" and the severity keyword "{urgent}".'
    else:
        reason = f'The description mentions "{evidence}", indicating {category.lower()}.'
    return {"complaint_id": complaint_id, "category": category, "priority": priority, "reason": reason, "flag": "" if category != "Other" else "NEEDS_REVIEW"}

def batch_classify(input_path: str, output_path: str):
    """Read, classify, and write one result row per input row."""
    results = []
    with open(input_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a description column")
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except (AttributeError, TypeError, ValueError):
                results.append({"complaint_id": row.get("complaint_id", ""), "category": "Other", "priority": "Standard", "reason": "The complaint row is malformed and needs review.", "flag": "NEEDS_REVIEW"})
    with open(output_path, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
