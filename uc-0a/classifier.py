"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row according to the enforcement rules in agents.md.

    Returns a dict with keys: ``category``, ``priority``, ``reason`` and ``flag``.
    The function follows the schema defined in the README and agents documentation.
    """
    # Extract description – the input CSV is expected to have a column named ``description``.
    description = row.get("description", "")
    description_lower = description.lower()

    # ---- Category detection -------------------------------------------------
    # Simple keyword‑based mapping to the allowed categories.
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "noise": "Noise",
        "road damage": "Road Damage",
        "heritage damage": "Heritage Damage",
        "heat hazard": "Heat Hazard",
        "drain blockage": "Drain Blockage",
    }
    category = "Other"
    matched_category_keywords = []
    for kw, cat in category_map.items():
        if kw in description_lower:
            category = cat
            matched_category_keywords.append(kw)
            break

    # ---- Priority detection -------------------------------------------------
    severity_keywords = [
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
    matched_severity = [kw for kw in severity_keywords if kw in description_lower]
    priority = "Urgent" if matched_severity else "Standard"

    # ---- Reason construction -----------------------------------------------
    reason_clauses = []
    if matched_category_keywords:
        reason_clauses.append(
            f"found keyword(s) {', '.join(matched_category_keywords)} indicating {category}"
        )
    if matched_severity:
        reason_clauses.append(
            f"severity keyword(s) {', '.join(matched_severity)} trigger Urgent priority"
        )
    if not reason_clauses:
        reason_clauses.append("no explicit clues; using default classification rules")
    reason = " ".join(reason_clauses)

    # ---- Flag handling ------------------------------------------------------
    flag = ""
    if category == "Other" or not description.strip():
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read an input CSV, classify each row using :func:`classify_complaint`,
    and write an output CSV that includes ``category``, ``priority``, ``reason``
    and ``flag`` columns.

    The function is tolerant to malformed rows – if classification raises an
    exception the row is written with ``category`` set to ``Other`` and the flag
    ``NEEDS_REVIEW``.
    """
    import csv

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        original_fieldnames = reader.fieldnames or []

    results = []
    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception:
            # Fallback for unexpected errors – ensures the pipeline never crashes.
            classification = {
                "category": "Other",
                "priority": "Standard",
                "reason": "classification error",
                "flag": "NEEDS_REVIEW",
            }
        results.append({**row, **classification})

    fieldnames = list(original_fieldnames) + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
