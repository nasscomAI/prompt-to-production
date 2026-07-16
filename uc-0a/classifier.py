"""
UC-0A — Complaint Classifier
Built per agents.md (RICE enforcement) and skills.md (classify_complaint, batch_classify).
"""
import argparse
import csv

# Allowed categories — exact strings only (agents.md enforcement rule 1)
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole"],
    "Flooding":        ["flood", "flooded", "flooding", "waterlog", "knee-deep"],
    "Streetlight":     ["streetlight", "street light", "lights out", "light out",
                         "flicker", "sparking", "dark at night", "unlit", "darkness",
                         "substation", "power outage", "wiring"],
    "Waste":           ["garbage", "trash", "waste", "dumped", "dead animal", "smell"],
    "Noise":           ["noise", "music", "loud", "drilling", "idling", "band playing"],
    "Road Damage":     ["road surface", "cracked", "sinking", "footpath",
                         "tiles broken", "manhole", "collapsed", "crater",
                         "paving", "cobblestone"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard":     ["heat", "heatwave", "heat wave", "melting", "temperature",
                         "hot surface", "sunstroke", "scorching"],
    "Drain Blockage":  ["drain blocked", "drain clogged", "drain"],
}

# Severity keywords that force Urgent (agents.md enforcement rule 2 / README)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Categories that default to Low priority absent a severity keyword
LOW_DEFAULT_CATEGORIES = {"Noise"}


def _find_matches(description: str, keyword_map: dict) -> dict:
    """Return {category: matched_keyword} for every category with a hit."""
    desc_lower = description.lower()
    matches = {}
    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw in desc_lower:
                matches[category] = kw
                break
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot determine category.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category_matches = _find_matches(description, CATEGORY_KEYWORDS)
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    if len(category_matches) == 1:
        ((category, matched_kw),) = category_matches.items()
        flag = ""
    elif len(category_matches) > 1:
        # Genuinely ambiguous between 2+ taxonomy values — do not guess.
        category = "Other"
        matched_kw = "/".join(sorted(category_matches.values()))
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        matched_kw = None
        flag = "NEEDS_REVIEW"

    if severity_hits:
        priority = "Urgent"
        reason_bits = [f"contains severity keyword '{severity_hits[0]}'"]
    else:
        priority = "Low" if category in LOW_DEFAULT_CATEGORIES else "Standard"
        reason_bits = []

    if matched_kw:
        reason_bits.insert(0, f"description cites '{matched_kw}' → {category}")
    elif flag == "NEEDS_REVIEW":
        reason_bits.insert(0, "no clear category keyword found in description")

    sentence = "; ".join(reason_bits)
    reason = sentence[0].upper() + sentence[1:] + "."

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
    A bad/malformed row is written with flag NEEDS_REVIEW instead of crashing the batch.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fields = reader.fieldnames or []
        rows = list(reader)

    output_fields = original_fields + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row-level failure during classification: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            out_row = {**row, **result}
            writer.writerow(out_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
