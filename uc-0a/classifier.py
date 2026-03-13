"""
UC-0A — Complaint Classifier
Classifies civic complaints using keyword matching per agents.md enforcement rules.
"""
import argparse
import csv

# ---------------------------------------------------------------------------
# Classification rules
# ---------------------------------------------------------------------------

# Order matters: first match wins. Each entry is (category, [keywords]).
CATEGORY_RULES = [
    ("Pothole",         ["pothole", "pot hole", "pothole"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlogg", "water log"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "lamppost", "light out", "lights out", "no light"]),
    ("Waste",           ["waste", "garbage", "trash", "dumping", "litter", "rubbish", "sewage overflow"]),
    ("Noise",           ["noise", "drilling", "loud", "sound", "horn", "idling", "engine on"]),
    ("Road Damage",     ["road collapsed", "road collapse", "crater", "road damage", "road broken", "road sunk", "collapse"]),
    ("Heritage Damage", ["heritage", "monument", "historical", "old city", "charminar"]),
    ("Heat Hazard",     ["heat", "temperature", "tar melting", "hot road", "heat wave"]),
    ("Drain Blockage",  ["drain block", "drain chok", "drain overflow", "drain full", "stormwater drain", "mosquito", "dengue"]),
]

# Keywords that force priority = Urgent (per agents.md)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _determine_category(description: str) -> tuple[str, str | None]:
    """Return (category, matched_keyword). matched_keyword is None → Other."""
    lower = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in lower:
                return category, kw
    return "Other", None


def _determine_priority(description: str) -> tuple[str, str | None]:
    """Return (priority, matched_urgent_keyword)."""
    lower = description.lower()
    for kw in URGENT_KEYWORDS:
        if kw in lower:
            return "Urgent", kw
    # Heuristic: descriptions with strong operational language → Standard
    standard_indicators = [
        "blocked", "flooded", "overflow", "collapsed", "crater",
        "abandoned", "suffering", "breeding", "risk", "concern",
    ]
    for kw in standard_indicators:
        if kw in lower:
            return "Standard", None
    return "Low", None


def classify_complaint(description: str) -> dict:
    """Classify a single complaint description.

    Returns a dict with keys: category, priority, reason, flag.

    The returned category will always be one of the allowed values.
    If the category cannot be determined, flag is set to "NEEDS_REVIEW".
    """

    description = (description or "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, cat_kw = _determine_category(description)
    priority, urg_kw = _determine_priority(description)

    # Build one-sentence reason citing the keyword found.
    if urg_kw:
        reason = (
            f"Complaint classified as {category} with Urgent priority "
            f"because the description contains '{urg_kw}'."
        )
    elif cat_kw:
        reason = (
            f"Complaint classified as {category} based on the keyword "
            f"'{cat_kw}' found in the description."
        )
    else:
        reason = "Category could not be determined from the description alone."

    # If the category cannot be determined, enforce review flag.
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def classify_complaint_row(row: dict) -> dict:
    """Classify a CSV row with at least complaint_id and description."""
    complaint_id = row.get("complaint_id", "").strip()
    result = classify_complaint(row.get("description", ""))
    result["complaint_id"] = complaint_id
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Skips malformed rows without crashing; always produces output file.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for line_num, row in enumerate(reader, start=2):
            try:
                result = classify_complaint_row(row)
                writer.writerow(result)
            except Exception as exc:
                # Log bad row and continue
                cid = row.get("complaint_id", f"row {line_num}")
                print(f"Warning: skipped {cid} — {exc}")
                writer.writerow({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Processing error: {exc}",
                    "flag": "NEEDS_REVIEW",
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")