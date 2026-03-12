"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    A simple rule-based implementation that matches keywords in the
    `description` field. This implementation enforces:
      * category must be one of the allowed strings (exact match).
      * priority is Urgent if any severity keywords are present.
      * reason cites specific words from the description.
      * flag is set to NEEDS_REVIEW when no clear category or multiple matches.
    """
    desc = row.get("description", "") or ""
    desc_lower = desc.lower()

    categories = [
        ("Pothole", ["pothole"]),
        ("Flooding", ["flood", "flooded"]),
        ("Streetlight", ["streetlight", "unlit"]),
        ("Waste", ["waste", "garbage", "bin"]),
        ("Noise", ["noise", "music", "drilling", "sound"]),
        ("Road Damage", ["road", "surface", "subsidence", "bubbling"]),
        ("Heritage Damage", ["heritage", "ancient", "histor"]),
        ("Heat Hazard", ["temperature", "heat", "melting"]),
        ("Drain Blockage", ["drain", "blocked", "sewer"]),
    ]
    matched = []
    for cat, keywords in categories:
        for kw in keywords:
            if kw in desc_lower:
                matched.append(cat)
                break

    # choose category or Other
    if len(matched) == 1:
        category = matched[0]
        flag = ""
    elif len(matched) > 1:
        category = matched[0]
        flag = "NEEDS_REVIEW"  # ambiguous
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # priority
    urgent_keywords = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            break

    # reason: pick first keyword found
    reason = ""
    for kw in urgent_keywords + [k for _, kws in categories for k in kws]:
        if kw in desc_lower:
            reason = f"Description mentions '{kw}'."
            break
    if not reason:
        reason = "No keyword found in description."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Rows that cannot be parsed are skipped with a warning. Output file will
    contain the original columns plus category, priority, reason, and flag.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []

        # add our output columns
        out_fields = fieldnames + ["category", "priority", "reason", "flag"]

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()

            for idx, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    out_row = row.copy()
                    out_row.update({
                        "category": result["category"],
                        "priority": result["priority"],
                        "reason": result["reason"],
                        "flag": result["flag"],
                    })
                    writer.writerow(out_row)
                except Exception as e:
                    # log error and continue
                    print(f"Warning: failed to classify row {idx}: {e}")
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
