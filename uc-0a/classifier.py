"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


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

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_PATTERNS = [
    ("Heritage Damage", ["heritage", "monument", "statue", "historic", "temple wall"]),
    ("Pothole", ["pothole", "crater", "tyre damage", "sinkhole"]),
    ("Flooding", ["flood", "flooded", "waterlogging", "water-logged", "underpass flooded"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "choked drain", "sewer blocked", "manhole overflow"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "flickering", "dark at night"]),
    ("Waste", ["garbage", "overflowing bins", "waste", "trash", "smell", "dumping"]),
    ("Noise", ["noise", "loudspeaker", "horn", "construction noise", "blaring"]),
    ("Heat Hazard", ["heat", "heatwave", "heat stroke", "dehydration", "extreme temperature"]),
    ("Road Damage", ["road damage", "road cracked", "broken road", "carriageway damaged", "road cave-in"]),
]


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    found = []
    for key in keywords:
        if key in text:
            found.append(key)
    return found

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row or {}).get("complaint_id", "")
    description = ((row or {}).get("description", "") or "").strip()
    text = description.lower()

    if not complaint_id:
        complaint_id = "UNKNOWN"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, cannot classify safely.",
            "flag": "NEEDS_REVIEW",
        }

    category_hits: dict[str, list[str]] = {}
    for category, keywords in CATEGORY_PATTERNS:
        hits = _find_keywords(text, keywords)
        if hits:
            category_hits[category] = hits

    if not category_hits:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No allowed category keywords found in description text."
    elif len(category_hits) > 1:
        # Multiple category hits are ambiguous for strict taxonomy.
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched = ", ".join(sorted(category_hits.keys()))
        reason = f"Description matches multiple categories: {matched}."
    else:
        category = next(iter(category_hits.keys()))
        flag = ""
        evidence = ", ".join(category_hits[category][:2])
        reason = f"Matched category '{category}' from description words: {evidence}."

    tokens = set(re.findall(r"[a-z]+", text))
    urgent = any(k in tokens for k in SEVERITY_KEYWORDS)
    priority = "Urgent" if urgent else "Standard"

    if priority == "Urgent":
        urgency_terms = sorted(k for k in SEVERITY_KEYWORDS if k in tokens)
        reason = f"{reason} Urgent due to severity keyword(s): {', '.join(urgency_terms)}."

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Computed category was outside allowed taxonomy; routed to Other."

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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8", newline="") as infile, open(
        output_path, "w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row or {}).get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
