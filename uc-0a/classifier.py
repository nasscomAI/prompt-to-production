"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os
import re


CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _categorise(desc: str) -> str:
    desc_lower = desc.lower()

    if re.search(r"\bpothole\b", desc_lower):
        return "Pothole"
    if re.search(r"\bflood", desc_lower) or "waterlogging" in desc_lower:
        return "Flooding"
    if re.search(r"\bheritage\b", desc_lower):
        return "Heritage Damage"
    if re.search(r"\bstreetlight", desc_lower):
        return "Streetlight"
    if "lights out" in desc_lower or "dark at night" in desc_lower or "flickering" in desc_lower or "sparking" in desc_lower:
        return "Streetlight"
    if re.search(r"\bgarbage\b", desc_lower) or \
       re.search(r"\bwaste\b", desc_lower) or \
       re.search(r"\bbin\b", desc_lower) or \
       re.search(r"\bdead animal\b", desc_lower):
        return "Waste"
    if re.search(r"\bnoise\b", desc_lower) or \
       re.search(r"\bmusic\b", desc_lower) or \
       re.search(r"\bloud\b", desc_lower):
        return "Noise"
    if re.search(r"\broad damage\b", desc_lower) or \
       re.search(r"\broad surface\b", desc_lower) or \
       (re.search(r"\bcracked\b", desc_lower) and re.search(r"\broad\b", desc_lower)) or \
       re.search(r"\bsinking\b", desc_lower) or \
       re.search(r"\bfootpath\b", desc_lower) or \
       re.search(r"\bmanhole\b", desc_lower):
        return "Road Damage"
    if re.search(r"\bheat\b", desc_lower):
        return "Heat Hazard"
    if re.search(r"\bdrain\b", desc_lower) or \
       re.search(r"\bblocked\b", desc_lower):
        return "Drain Blockage"

    return "Other"


def _priority(desc: str) -> str:
    desc_lower = desc.lower()
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", desc_lower):
            return "Urgent"
    return "Standard"


def _reason(desc: str, category: str, urgent: bool) -> str:
    if not desc or len(desc.strip()) < 5:
        return "Description too ambiguous to classify"
    words = [w for w in desc.replace(",", " ").replace(".", " ").split() if len(w) > 3]
    cited = " ".join(words[:8])
    if urgent:
        return f"Complaint describes '{cited}' which matches urgent severity keywords."
    return f"Complaint describes '{cited}' classified as {category}."


def _flag(category: str, desc: str) -> str:
    if category == "Other" or not desc or len(desc.strip()) < 5:
        return "NEEDS_REVIEW"
    return ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description too ambiguous to classify",
            "flag": "NEEDS_REVIEW",
        }

    category = _categorise(description)
    priority = _priority(description)
    reason = _reason(description, category, priority == "Urgent")
    flag = _flag(category, description)

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
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no columns")
        if "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a 'description' column")

        rows = list(reader)

    if not rows:
        raise ValueError("Input CSV is empty")

    output_fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()

        for row in rows:
            result = classify_complaint(row)
            row.update({
                "category": result["category"],
                "priority": result["priority"],
                "reason": result["reason"],
                "flag": result["flag"],
            })
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
