"""
UC-0A — Complaint Classifier
Rule-based classifier implementing RICE enforcement from agents.md.
"""
import argparse
import csv
import sys

# Severity keywords that must trigger Urgent (agents.md enforcement rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

# Category keyword patterns (agents.md enforcement rule 1 — exact allowed values)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flooded", "flood"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "sparking"],
    "Waste": ["garbage", "dead animal", "bulk waste", "overflowing", "dumped"],
    "Noise": ["noise", "music", "loud", "wedding"],
    "Road Damage": ["road surface", "footpath", "sinking", "cracked", "broken", "upturned"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heatwave", "heat"],
    "Drainage Blockage": ["manhole", "sewer", "drain blocked", "blocked drain"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based keyword matching.

    RICE enforcement from agents.md:
    1. Category must be exactly one of the allowed list — no variations, no synonyms
    2. Priority must be Urgent if description contains severity keywords
    3. Every output row must include a reason field citing specific words
    4. If category genuinely ambiguous — output Other + NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", "")
    desc = row.get("description", "")
    desc_lower = desc.lower()

    # --- Category detection (enforcement 1 & 4) ---
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw in desc_lower)
        if match_count > 0:
            scores[cat] = match_count

    if not scores:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        sorted_cats = sorted(scores.items(), key=lambda x: -x[1])
        top_cat, top_score = sorted_cats[0]
        if len(sorted_cats) > 1 and sorted_cats[1][1] >= top_score:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = top_cat
            flag = ""

    # --- Priority detection (enforcement 2) ---
    priority = "Standard"
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            matched_severity.append(kw)
            priority = "Urgent"

    # --- Reason generation (enforcement 3 — cite specific words) ---
    all_matched = []
    if category in CATEGORY_KEYWORDS:
        all_matched = [kw for kw in CATEGORY_KEYWORDS[category] if kw in desc_lower]
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    cited = all_matched[:3] + matched_severity[:3]
    if cited:
        reason = f"Classified based on keywords: {', '.join(cited)}"
    elif scores and category == "Other":
        other_matches = []
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in desc_lower:
                    other_matches.append(f"{cat}:{kw}")
        if other_matches:
            reason = f"Ambiguous — multiple categories matched: {', '.join(other_matches[:4])}"
        else:
            reason = "Description did not match any known category"
    else:
        reason = "Description did not match any known category"

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
    Handles errors gracefully — logs bad rows, continues processing.
    """
    rows = []
    errors = []

    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    row["category"] = result["category"]
                    row["priority"] = result["priority"]
                    row["reason"] = result["reason"]
                    row["flag"] = result["flag"]
                    rows.append(row)
                except Exception as e:
                    errors.append(f"Row {i} (ID: {row.get('complaint_id', 'unknown')}): {e}")
                    row["category"] = "Other"
                    row["priority"] = "Standard"
                    row["reason"] = f"Error during classification: {e}"
                    row["flag"] = "NEEDS_REVIEW"
                    rows.append(row)
    except FileNotFoundError:
        print(f"Error: Input file not found — {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    output_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)

    if errors:
        print("Warnings during classification:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)

    print(f"Processed {len(rows)} rows. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
