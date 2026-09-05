"""
UC-0A — Complaint Classifier
Classifies citizen complaints into exact taxonomy categories, priorities,
and reasons, enforcing the RICE rules from agents.md.
"""
import argparse
import csv

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
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _has_severity_keyword(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in SEVERITY_KEYWORDS)


def _categorize(description: str) -> str:
    lowered = description.lower()
    if any(kw in lowered for kw in ["pothole", "tyre damage", "tyre"]):
        return "Pothole"
    if any(kw in lowered for kw in ["flood", "flooded", "flooding", "water", "inaccessible"]):
        return "Flooding"
    if any(kw in lowered for kw in ["streetlight", "lights out", "light out", "lighting"]):
        return "Streetlight"
    if any(kw in lowered for kw in ["garbage", "waste", "dead animal", "bins", "dumped", "bulk waste"]):
        return "Waste"
    if any(kw in lowered for kw in ["music", "noise", "loud", "sparking"]):
        return "Noise"
    if any(kw in lowered for kw in ["road surface", "road damage", "cracked", "sinking", "manhole", "footpath", "tiles"]):
        return "Road Damage"
    if any(kw in lowered for kw in ["heritage", "old city", "historic"]):
        return "Heritage Damage"
    if any(kw in lowered for kw in ["heat", "heatwave", "sunstroke", "temperature", "degrees", "lakh", "unbearable"]):
        return "Heat Hazard"
    if any(kw in lowered for kw in ["drain", "drainage"]):
        return "Drain Blockage"
    return "Other"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()

    category = _categorize(description)
    priority = "Urgent" if _has_severity_keyword(description) else "Standard"
    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = _build_reason(description, category, priority)

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(description: str, category: str, priority: str) -> str:
    lowered = description.lower()
    cited = []
    for kw in SEVERITY_KEYWORDS:
        if kw in lowered:
            cited.append(kw)
    parts = [f'Categorized as {category} based on "{description[:50]}"']
    if cited:
        parts.append(f"severity keyword(s) {', '.join(cited)}")
    return "; ".join(parts) + "."


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):
            try:
                if not (row.get("description") or "").strip():
                    row["description"] = ""
                result = classify_complaint(row)
                rows.append(result)
            except Exception:
                rows.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Unable to classify row (line " + str(line_num) + "), please review.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
