"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = [
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


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    lowered = description.lower()
    category = infer_category(description)
    priority = "Urgent" if any(keyword in lowered for keyword in SEVERITY_KEYWORDS) else "Standard"
    flag = "NEEDS_REVIEW" if should_flag(description, category) else ""
    reason = build_reason(description, category)

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def infer_category(description: str) -> str:
    lowered = description.lower()

    if any(term in lowered for term in ["pothole", "tyre damage"]):
        return "Pothole"
    if any(term in lowered for term in ["flood", "flooded", "water", "rain", "inundated"]):
        return "Flooding"
    if any(term in lowered for term in ["streetlight", "lights out", "flickering", "sparking", "electrical"]):
        return "Streetlight"
    if any(term in lowered for term in ["garbage", "waste", "overflowing bins", "dumped", "bulk waste"]):
        return "Waste"
    if any(term in lowered for term in ["music", "noise", "loud", "midnight"]):
        return "Noise"
    if any(term in lowered for term in ["road", "cracked", "surface", "tiles broken", "upturned", "manhole", "footpath"]):
        return "Road Damage"
    if any(term in lowered for term in ["heritage", "historic"]):
        return "Heritage Damage"
    if any(term in lowered for term in ["heat", "hot", "temperature", "sun"]):
        return "Heat Hazard"
    if any(term in lowered for term in ["drain", "blocked", "blockage"]):
        return "Drain Blockage"
    return "Other"


def should_flag(description: str, category: str) -> bool:
    lowered = description.lower()
    if not description:
        return True
    if category == "Other":
        return True
    if "safety concern" in lowered or "health concern" in lowered:
        return True

    category_hits = [
        name.lower()
        for name in ALLOWED_CATEGORIES
        if name.lower() in lowered and name.lower() not in {"other"}
    ]
    if len(category_hits) > 1:
        return True
    return False


def build_reason(description: str, category: str) -> str:
    lowered = description.lower()
    if not description:
        return "No description was supplied, so the category is treated as Other."

    evidence_terms = [
        "pothole",
        "flooded",
        "streetlight",
        "garbage",
        "waste",
        "music",
        "noise",
        "cracked",
        "heritage",
        "heat",
        "drain",
        "manhole",
        "hazard",
        "children",
        "injury",
        "school",
        "hospital",
        "fell",
        "collapse",
    ]
    found_terms = [term for term in evidence_terms if term in lowered]
    if found_terms:
        quoted_terms = ", ".join(f"'{term}'" for term in found_terms[:3])
        return f"The description cites {quoted_terms}, which supports the {category} classification."

    snippet = description.split(".")[0][:80]
    return f"The description says '{snippet}' and supports the {category} classification."


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(input_path, "r", encoding="utf-8", newline="") as src:
        reader = csv.DictReader(src)
        rows = list(reader)

    with open(output_path, "w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The row could not be parsed reliably, so it was marked as Other.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
