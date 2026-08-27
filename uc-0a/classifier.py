"""
UC-0A — Complaint Classifier
Rule-based implementation guided by agents.md + skills.md (RICE enforcement).
"""
import argparse
import csv
import sys
from typing import Optional

# ── Schema constants ────────────────────────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# Category keyword map — checked in order; first match wins
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Pothole",         ["pothole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlog", "inundated", "stranded", "knee-deep"]),
    ("Drain Blockage",  ["drain blocked", "drain block", "blocked drain", "blocked gutter"]),
    ("Streetlight",     ["streetlight", "street light", "lamp", "light out", "lights out", "sparking", "flickering"]),
    ("Noise",           ["noise", "music", "loud", "midnight", "sound"]),
    ("Road Damage",     ["cracked", "sinking", "surface", "manhole", "broken", "upturned", "footpath", "tile"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard",     ["heat", "temperature", "hot", "summer"]),
    ("Waste",           ["garbage", "waste", "dump", "dumped", "overflowing bin", "dead animal", "smell", "health concern"]),
]


# ── Core skill: classify_complaint ──────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Enforces all rules defined in agents.md.
    """
    complaint_id: str = row.get("complaint_id", "").strip()
    description: str = row.get("description", "").strip()

    # Error path — empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was empty or missing.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Category detection ───────────────────────────────────────────────────
    matched_category: Optional[str] = None
    matched_keyword: Optional[str] = None

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = category
                matched_keyword = kw
                break
        if matched_category:
            break

    # Ambiguity flag
    flag = ""
    if matched_category is None:
        matched_category = "Other"
        flag = "NEEDS_REVIEW"

    # ── Priority detection (severity keywords override everything) ───────────
    triggered_severity: Optional[str] = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            triggered_severity = kw
            break

    if triggered_severity:
        priority = "Urgent"
        reason = (
            f"Classified as '{matched_category}' because the description mentions "
            f"'{matched_keyword or matched_category.lower()}'; "
            f"priority set to Urgent due to severity keyword '{triggered_severity}'."
        )
    else:
        priority = "Standard"
        reason = (
            f"Classified as '{matched_category}' because the description mentions "
            f"'{matched_keyword or 'general ' + matched_category.lower()}'."
        )

    # Low priority heuristic — no urgency signals, very routine phrasing
    urgency_signals = ["immediate", "urgent", "emergency", "danger", "risk", "unsafe"]
    if priority == "Standard" and not any(s in desc_lower for s in urgency_signals):
        if matched_category in ("Noise",):
            priority = "Low"

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Core skill: batch_classify ───────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    Skips malformed rows (logged to stderr). Always writes output file.
    """
    OUTPUT_FIELDS = [
        "complaint_id", "date_raised", "city", "ward", "location",
        "description", "reported_by", "days_open",
        "category", "priority", "reason", "flag",
    ]

    results: list[dict] = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader, start=2):  # row 1 = header
            try:
                classification = classify_complaint(row)
                combined = {**row, **classification}
                results.append(combined)
            except Exception as exc:
                print(f"[WARN] Skipping row {i} due to error: {exc}", file=sys.stderr)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
