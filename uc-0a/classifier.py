"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
from typing import Dict, Tuple

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag.

    This function applies the UC-0A schema and the RICE enforcement rules from
    agents.md and skills.md. It uses keyword matching to assign an exact
    allowed category, promote urgent complaints, and produce a one-sentence reason.
    """
    # Allowed categories are enforced via schema_enforcer later.
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

    # Category mapping is intentionally conservative to reduce hallucination.
    CATEGORY_KEYWORDS = {
        "Pothole": ["pothole", "hole in the road", "open pothole"],
        "Flooding": ["flood", "flooding", "waterlogged", "water on the road", "overflow"],
        "Streetlight": ["streetlight", "street light", "lamp", "light not working", "bulb"],
        "Waste": ["garbage", "trash", "waste", "dump", "litter"],
        "Noise": ["noise", "loud", "shouting", "music", "construction noise"],
        "Road Damage": ["road damage", "crack", "broken road", "asphalt", "surface"],
        "Heritage Damage": ["heritage", "monument", "statue", "historic", "temple"],
        "Heat Hazard": ["heat", "hot", "scorching", "heatwave", "burn"],
        "Drain Blockage": ["drain", "drainage", "blocked drain", "sewer", "gully"]
    }

    # Severity keywords force Urgent priority when present.
    SEVERITY_KEYWORDS = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]

    # Normalize the complaint description for matching.
    description = (row.get("description") or "").strip()
    desc_low = description.lower()

    if not description:
        # Missing description is considered ambiguous and needs review.
        return {
            "category": "Other",
            "priority": "",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    # Find all matching categories based on keyword presence.
    matches = []
    matched_phrase = None
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc_low:
                matches.append(cat)
                if not matched_phrase:
                    matched_phrase = kw
                break

    # If exactly one category matches, use it; otherwise treat as ambiguous.
    if len(matches) == 1:
        category = matches[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Default priority is Standard, upgrade to Urgent on severity keywords.
    priority = "Standard"
    for sk in SEVERITY_KEYWORDS:
        if sk in desc_low:
            priority = "Urgent"
            if not matched_phrase:
                matched_phrase = sk
            break

    # Build a one-sentence reason that cites text from the description.
    if matched_phrase:
        reason = f"Mentions '{matched_phrase}' in description."
    else:
        snippet = " ".join(description.split()[:6])
        reason = f"Mentions '{snippet}' in description."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    This function preserves the input columns, appends the required UC-0A
    classification columns, and writes the final CSV atomically to avoid
    partial writes on failure.
    """
    temp_out = output_path + ".tmp"
    rows_processed = 0
    flagged_count = 0
    errors = 0

    with open(input_path, newline='', encoding='utf-8') as inf:
        reader = csv.DictReader(inf)
        input_fieldnames = reader.fieldnames or []
        out_fieldnames = list(input_fieldnames) + ["category", "priority", "reason", "flag"]

        with open(temp_out, 'w', newline='', encoding='utf-8') as outf:
            writer = csv.DictWriter(outf, fieldnames=out_fieldnames)
            writer.writeheader()

            for row in reader:
                rows_processed += 1
                try:
                    classified = classify_complaint(row)
                except Exception:
                    # If classification fails, preserve the row and flag for review.
                    errors += 1
                    classified = {
                        "category": "Other",
                        "priority": "",
                        "reason": "Classification error",
                        "flag": "NEEDS_REVIEW",
                    }

                # Validate the classifier output against the expected schema.
                validated = schema_enforcer(classified)

                if validated.get("flag") == "NEEDS_REVIEW":
                    flagged_count += 1

                out_row = dict(row)
                out_row.update({
                    "category": validated.get("category", "Other"),
                    "priority": validated.get("priority", ""),
                    "reason": validated.get("reason", ""),
                    "flag": validated.get("flag", ""),
                })

                writer.writerow(out_row)

    # Replace the destination file atomically to avoid partial writes.
    os.replace(temp_out, output_path)

    summary = {"rows_processed": rows_processed, "flagged_count": flagged_count, "errors": errors}
    return summary


def schema_enforcer(classified: Dict[str, str]) -> Dict[str, str]:
    """Basic rule-based validator and normalizer for classifier outputs."""
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
    ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low", ""]

    out = {
        # Default missing or blank values to safe fallbacks.
        "category": (classified.get("category") or "Other").strip(),
        "priority": (classified.get("priority") or "Standard").strip(),
        "reason": (classified.get("reason") or "").strip(),
        "flag": (classified.get("flag") or "").strip(),
    }

    # If the category is invalid, classify it as Other and flag for review.
    if out["category"] not in ALLOWED_CATEGORIES:
        out["category"] = "Other"
        out["flag"] = "NEEDS_REVIEW"

    # If priority is invalid, fall back to Standard.
    if out["priority"] not in ALLOWED_PRIORITIES:
        out["priority"] = "Standard"

    # Ensure reason is present; otherwise flag the output.
    if not out["reason"]:
        out["flag"] = "NEEDS_REVIEW"
        out["reason"] = "No reason provided"

    # Guarantee the flag key exists in all outputs.
    if out.get("flag") is None:
        out["flag"] = ""

    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
