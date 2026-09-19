"""UC-0A deterministic complaint classifier."""
import argparse
import csv
import re
from typing import Dict

ALLOWED = ("Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other")
URGENT_TERMS = ("injury", "child", "school", "hospital", "hospitalised", "ambulance", "fire", "hazard", "fell", "collapse", "collapsed")

def _evidence(text: str, terms):
    found = [term for term in terms if re.search(r"\b" + re.escape(term) + r"\b", text, re.I)]
    return found

def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "") or "").strip()
    if not description:
        return {"complaint_id": complaint_id, "category": "Other", "priority": "Standard", "reason": "Description is missing, so no category can be supported.", "flag": "NEEDS_REVIEW"}
    text = description.lower()
    category = "Other"
    category_terms = []
    if _evidence(text, ("heritage", "historic", "monument", "old city")):
        category, category_terms = "Heritage Damage", ["heritage", "historic", "monument", "old city"]
    elif _evidence(text, ("streetlight", "street light", "lamp post", "lamp", "dark road")):
        category, category_terms = "Streetlight", ["streetlight", "street light", "lamp post", "lamp", "dark road"]
    elif _evidence(text, ("drilling", "noise", "loud", "horn", "sound")):
        category, category_terms = "Noise", ["drilling", "noise", "loud", "horn", "sound"]
    elif _evidence(text, ("garbage", "waste", "rubbish", "litter", "overflow", "trash")):
        category, category_terms = "Waste", ["garbage", "waste", "rubbish", "litter", "overflow", "trash"]
    elif _evidence(text, ("pothole", "potholes")):
        category, category_terms = "Pothole", ["pothole", "potholes"]
    elif _evidence(text, ("collapsed", "collapse", "crater", "road broken", "road damage")):
        category, category_terms = "Road Damage", ["collapsed", "collapse", "crater", "road broken", "road damage"]
    elif _evidence(text, ("drain blocked", "drain completely blocked", "drain", "stormwater drain", "main drain", "blocked drain", "drainage")):
        category, category_terms = "Drain Blockage", ["drain", "blocked", "stormwater", "drainage"]
    elif _evidence(text, ("flood", "flooded", "flooding", "rainwater", "underpass")):
        category, category_terms = "Flooding", ["flood", "flooded", "flooding", "rainwater", "underpass"]
    elif _evidence(text, ("heat", "hot", "temperature")):
        category, category_terms = "Heat Hazard", ["heat", "hot", "temperature"]
    urgent = _evidence(text, URGENT_TERMS)
    priority = "Urgent" if urgent else "Standard"
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    evidence = _evidence(text, category_terms) or [category]
    reason = f"Classified as {category} because the description contains {', '.join(repr(x) for x in evidence[:3])}."
    if urgent:
        reason += f" Priority is Urgent because it contains {', '.join(repr(x) for x in urgent[:3])}."
    return {"complaint_id": complaint_id, "category": category, "priority": priority, "reason": reason, "flag": flag}

def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {"complaint_id": str(row.get("complaint_id", "")), "category": "Other", "priority": "Standard", "reason": f"Row could not be classified safely: {exc}.", "flag": "NEEDS_REVIEW"}
            writer.writerow(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
