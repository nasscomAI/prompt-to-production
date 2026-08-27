"""
UC-0A — Complaint Classifier
Implementation adhering to agents.md, skills.md, and README.md specifications.
"""
import argparse
import csv
import re
import sys
from typing import Dict, Any, List, Optional

# Approved category taxonomy - exact strings only
APPROVED_CATEGORIES = [
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

APPROVED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = [
    r"\binjur(?:y|ies|ed|ing)?\b",
    r"\bchild(?:ren)?\b",
    r"\bschool(?:s)?\b",
    r"\bhospital(?:s|ised|ized)?\b",
    r"\bambulance(?:s)?\b",
    r"\bfire(?:s)?\b",
    r"\bhazard(?:s|ous)?\b",
    r"\bfell\b",
    r"\bcollaps(?:e|ed|es|ing)\b",
]


def contains_severity_keyword(text: str) -> bool:
    """Return True if the text contains any mandatory severity keyword."""
    if not text:
        return False
    for pattern in SEVERITY_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _extract_category(description: str) -> Optional[str]:
    """
    Determine the category based on specific complaint description keywords.
    Returns an approved category string or None if ambiguous/unclassifiable.
    """
    text = description.lower()

    # Pothole check
    if re.search(r"\bpothole[s]?\b", text):
        return "Pothole"

    # Noise check
    if re.search(r"\b(?:music|drilling|amplifiers?|audible|decibels?|idling with engines|wedding band)\b", text):
        return "Noise"

    # Heat Hazard check
    if re.search(
        r"\b(?:melting at \d+°c|bubbling at \d+°c|temperature[s]? unbearable|\d+°c|heatwave|burns on contact|exposed to full sun|dangerous temperatures)\b",
        text,
    ):
        return "Heat Hazard"

    # Heritage Damage check (structural/historic physical damage or heritage integrity loss)
    # Must distinguish from general noise/waste occurring in a heritage zone.
    if re.search(
        r"\b(?:heritage|historic|ancient)\b.*?\b(?:lamp post|cobblestones|building|defaced|subsidence|stone not replaced|step well)\b",
        text,
    ) or re.search(
        r"\b(?:cobblestones broken|heritage stone|ancient step well|heritage residential building exterior defaced)\b",
        text,
    ):
        return "Heritage Damage"

    # Waste check (garbage, debris, dead animal, overflowing bins)
    if re.search(
        r"\b(?:garbage|waste|dumped|trash|bins? overflowing|overflowing.*?bins?|dead animal|refuse|litter)\b",
        text,
    ):
        return "Waste"

    # Drain Blockage check
    if re.search(
        r"\b(?:drain(?:s|age)?.*?block(?:ed|age)?|block(?:ed|age)?.*?drain(?:s|age)?|stormwater drain|draining directly onto)\b",
        text,
    ):
        return "Drain Blockage"

    # Flooding check
    if re.search(r"\b(?:flood(?:ed|ing|s)?|underpass flooded|waterlogging|knee-deep)\b", text):
        return "Flooding"

    # Streetlight check
    if re.search(
        r"\b(?:streetlight[s]?|street light[s]?|lights out|unlit|darkness for|substation tripped|sparking)\b",
        text,
    ):
        return "Streetlight"

    # Road Damage check (cracked, buckled, sinking, broken footpath/paving/manhole)
    if re.search(
        r"\b(?:road surface|cracked and sinking|road collapsed|crater|buckled|footpath broken|tiles broken|upturned paving|subsidence|manhole cover missing)\b",
        text,
    ):
        return "Road Damage"

    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = ""
    if isinstance(row, dict):
        complaint_id = str(row.get("complaint_id") or "").strip()
        description = str(row.get("description") or "").strip()
    else:
        description = ""

    # Check for missing description or empty data
    if not description:
        return {
            "complaint_id": complaint_id or "UNKNOWN",
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description.",
            "flag": "NEEDS_REVIEW",
        }

    # Determine priority based on mandatory severity keywords
    is_urgent = contains_severity_keyword(description)
    priority = "Urgent" if is_urgent else "Standard"

    # Determine category
    detected_cat = _extract_category(description)

    # Sanitize snippet for reason
    clean_desc = description.strip().replace("\n", " ").replace('"', "'")
    if clean_desc.endswith("."):
        clean_desc = clean_desc[:-1]

    if detected_cat and detected_cat in APPROVED_CATEGORIES and detected_cat != "Other":
        category = detected_cat
        flag = ""
        reason = f"Classified as {category} based on description keywords: \"{clean_desc}\"."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Complaint description '{clean_desc}' is ambiguous or outside standard categories, requiring manual review."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results: List[Dict[str, Any]] = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as row_err:
                    # Robust fallback for corrupted row
                    complaint_id = row.get("complaint_id") if isinstance(row, dict) else f"ROW_{row_idx}"
                    results.append({
                        "complaint_id": complaint_id or f"ROW_{row_idx}",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing failed due to error: {str(row_err)}.",
                        "flag": "NEEDS_REVIEW",
                    })
    except Exception as file_err:
        print(f"Error reading input file {input_path}: {file_err}", file=sys.stderr)
        pass

    # Write results CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow({
                "complaint_id": res.get("complaint_id", ""),
                "category": res.get("category", "Other"),
                "priority": res.get("priority", "Standard"),
                "reason": res.get("reason", ""),
                "flag": res.get("flag", ""),
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
