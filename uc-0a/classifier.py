"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, Tuple

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # Retrieve description (fallback to join of all values if key missing)
    description = (row.get("description") or "").strip()
    if not description:
        # Try alternative fields
        for k in ("text", "complaint", "details"):
            if row.get(k):
                description = str(row.get(k)).strip()
                break

    text = description.lower()

    # Category keywords (simple deterministic mappings)
    CATEGORY_KEYWORDS = {
        "Pothole": ["pothole", "hole in road", "big hole"],
        "Flooding": ["flood", "water logging", "waterlogged", "overflow"],
        "Streetlight": ["streetlight", "light not working", "lamp post", "dark street"],
        "Waste": ["garbage", "trash", "dump", "waste", "bin"],
        "Noise": ["noise", "loud", "construction noise", "honking"],
        "Road Damage": ["road damage", "broken road", "crack in road"],
        "Heritage Damage": ["heritage", "monument", "historical building", "vandal"],
        "Heat Hazard": ["heat", "hot", "heatwave", "hot water"],
        "Drain Blockage": ["drain", "blocked drain", "sewer", "drainage blocked"]
    }

    SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    LOW_PRIORITY_KEYWORDS = ["minor", "cosmetic", "small", "low priority", "nuisance"]

    matched_categories = set()
    matched_terms = []

    # Find keyword matches (word-boundary aware)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            # use simple substring and word boundary regex to avoid partial matches
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                matched_categories.add(category)
                matched_terms.append(kw)

    # Determine category and flag
    if len(matched_categories) == 1:
        category = next(iter(matched_categories))
        flag = ""
    elif len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # Multiple categories matched -> ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Determine priority
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            priority = "Urgent"
            break
    else:
        for kw in LOW_PRIORITY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                priority = "Low"
                break

    # Build reason: must be one sentence and cite specific words
    if description == "":
        reason = "NEEDS_REVIEW: empty description"
    elif matched_terms:
        # use unique matched terms and limit length
        unique_terms = []
        for t in matched_terms:
            if t not in unique_terms:
                unique_terms.append(t)
        cited = ", ".join([f"'{t}'" for t in unique_terms[:3]])
        reason = f"Mentions {cited} in description."
    else:
        reason = "NEEDS_REVIEW: no category keywords found in description"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    rows_processed = 0
    rows_flagged = 0
    errors = 0

    try:
        with open(input_path, newline='', encoding='utf-8') as inf:
            reader = csv.DictReader(inf)
            input_fieldnames = reader.fieldnames or []
            out_fieldnames = list(input_fieldnames) + ["category", "priority", "reason", "flag"]

            with open(output_path, 'w', newline='', encoding='utf-8') as outf:
                writer = csv.DictWriter(outf, fieldnames=out_fieldnames)
                writer.writeheader()

                for row in reader:
                    rows_processed += 1
                    try:
                        result = classify_complaint(row)
                        out_row = dict(row)
                        out_row.update({
                            "category": result.get("category", "Other"),
                            "priority": result.get("priority", "Standard"),
                            "reason": result.get("reason", "NEEDS_REVIEW"),
                            "flag": result.get("flag", "")
                        })
                        if out_row.get("flag"):
                            rows_flagged += 1
                        writer.writerow(out_row)
                    except Exception as e:
                        errors += 1
                        # On per-row failure, write a best-effort row
                        out_row = dict(row)
                        out_row.update({
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"NEEDS_REVIEW: error processing row: {e}",
                            "flag": "NEEDS_REVIEW"
                        })
                        rows_flagged += 1
                        writer.writerow(out_row)

    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return {"rows_processed": 0, "rows_flagged": 0, "errors": 1}
    except Exception as e:
        print(f"Failed to process file: {e}")
        return {"rows_processed": rows_processed, "rows_flagged": rows_flagged, "errors": errors + 1}

    summary = {"rows_processed": rows_processed, "rows_flagged": rows_flagged, "errors": errors}
    print(f"Processed {rows_processed} rows, flagged {rows_flagged}, errors {errors}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
