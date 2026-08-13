"""
UC-0A — Complaint Classifier
Classifies citizen complaints into category + priority + reason + flag.
Rules come from agents.md (RICE) and skills.md (UC-0A).
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered category rules — first match wins.
CATEGORY_RULES = [
    ("Pothole",        ["pothole"]),
    ("Flooding",       ["flood", "rainwater", "knee-deep", "standing in water", "submerged"]),
    ("Streetlight",    ["streetlight", "street light", "lights out", "light out",
                        "unlit", "substation", "wiring theft", "darkness"]),
    ("Drain Blockage", ["drain"]),
    ("Noise",          ["music", "amplifier", "band", "noise", "drilling", "drill"]),
    ("Waste",          ["waste", "garbage", "trash", "dead animal", "bins"]),
    ("Heritage Damage", ["heritage", "historic", "ancient", "museum",
                         "palace", "cobblestone", "step well"]),
    ("Heat Hazard",    ["melting", "bubbling", "temperature", "\u00b0c",
                        "unbearable", "storing heat", "burns"]),
    ("Road Damage",    ["road", "footpath", "paving", "pavement", "manhole",
                        "subsided", "buckled", "surface", "bridge"]),
]


def _excerpt(original: str, term: str) -> str:
    """Return a short window of the original description around the matched term."""
    low = original.lower()
    idx = low.find(term)
    if idx == -1:
        return term
    start = max(0, idx - 15)
    end = min(len(original), idx + len(term) + 25)
    return original[start:end].strip()


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    original = str(row.get("description") or "")
    desc = original.lower()
    complaint_id = str(row.get("complaint_id") or "").strip()

    if not complaint_id or not desc.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Row malformed: complaint_id or description missing.",
            "flag": "NEEDS_REVIEW",
        }

    category = "Other"
    matched_term = None
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc:
                category = cat
                matched_term = kw
                break
        if matched_term is not None:
            break

    priority = "Standard"
    severity_hit = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            severity_hit = kw
            break
    if severity_hit is not None:
        priority = "Urgent"

    if category == "Other":
        reason = "Category not determinable from description alone; flagged NEEDS_REVIEW."
    else:
        reason = (f"{category} because description cites '{_excerpt(original, matched_term)}'"
                  + (f"; severity keyword '{severity_hit}' triggers Urgent." if severity_hit else "."))

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if category == "Other" else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    output_rows = [classify_complaint(row) for row in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["complaint_id", "category", "priority", "reason", "flag"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
