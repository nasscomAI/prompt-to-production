"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.

Rule-based implementation — no LLM, no API key, no external dependencies.
Uses only Python standard library.

Run:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv

# ---------------------------------------------------------------------------
# Taxonomy constants (agents.md / README)
# ---------------------------------------------------------------------------

# Maps each allowed category to keywords that signal it (all lowercase)
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "pot hole", "tyre damage", "tyre puncture"],
    "Flooding":        ["flood", "flooded", "flooding", "waterlogged", "water logging",
                        "inundated", "knee-deep", "stranded", "standing water"],
    "Streetlight":     ["streetlight", "street light", "lamp", "light out", "lights out",
                        "flickering", "sparking", "dark", "no light", "unlit",
                        "wiring", "no lighting", "not lit"],
    "Waste":           ["garbage", "waste", "rubbish", "trash", "bins", "litter",
                        "dumped", "dump", "overflowing", "smell", "dead animal"],
    "Noise":           ["noise", "music", "sound", "loud", "midnight", "disturbance"],
    "Road Damage":     ["road surface", "cracked", "sinking", "road damage", "broken road",
                        "damaged road", "utility work", "manhole", "footpath", "tiles broken",
                        "upturned", "road crack"],
    "Heritage Damage": ["heritage", "historical", "monument", "old city", "heritage street"],
    "Heat Hazard":     ["heat", "temperature", "hot", "scorching", "heat hazard",
                        "melting", "tarmac", "sticking", "sun exposure", "exposed to sun"],
    "Drain Blockage":  ["drain", "drainage", "blocked drain", "drain blocked", "sewer",
                        "sewage", "overflow drain"],
}

# Severity keywords that must trigger Urgent (agents.md enforcement rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the description field only.

    Input:  dict with keys complaint_id, date_raised, city, ward, location,
            description, reported_by, days_open. Only description is used.
    Output: dict with keys complaint_id, category, priority, reason, flag.
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Category matching ---
    matched_categories = []
    matched_keywords = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            matched_categories.append(category)
            matched_keywords[category] = hits

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = (
            f"Description mentions '{matched_keywords[category][0]}', "
            f"indicating a {category} complaint."
        )
    elif len(matched_categories) > 1:
        # Ambiguous — take first match but flag for review
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason = (
            f"Description matches multiple categories "
            f"({', '.join(matched_categories)}); flagged for review."
        )
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description did not match any known category keywords; flagged for review."

    # --- Priority: hard-enforce severity keywords (agents.md enforcement rule 2) ---
    severity_hit = next((kw for kw in SEVERITY_KEYWORDS if kw in desc_lower), None)
    if severity_hit:
        priority = "Urgent"
        reason = (
            f"Description contains severity keyword '{severity_hit}'. "
            + reason
        )
    else:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint per row, write results CSV.

    Input columns:  complaint_id, date_raised, city, ward, location,
                    description, reported_by, days_open
    Output columns: complaint_id, category, priority, reason, flag
    Continues on row-level errors — does not halt the batch.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as err:
                print(f"  [WARN] Row {row.get('complaint_id', '?')} failed: {err}")
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row processing error.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
