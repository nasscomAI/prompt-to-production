"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and flag
using R.I.C.E enforcement rules from agents.md.
"""
import argparse
import csv
import re

# ── Classification Schema ──────────────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword-to-category mapping (order matters — first match wins)
CATEGORY_RULES = [
    # Pothole
    (["pothole", "pot hole", "pot-hole"], "Pothole"),
    # Drain Blockage (before Flooding so "drain blocked" maps here)
    (["drain block", "drain clog", "blocked drain", "manhole", "sewer block"], "Drain Blockage"),
    # Flooding
    (["flood", "waterlog", "water log", "water-log", "submerge", "inundat",
      "knee-deep", "knee deep", "stranded"], "Flooding"),
    # Streetlight
    (["streetlight", "street light", "street-light", "lights out",
      "light out", "lamp post", "lamppost", "flickering", "sparking"], "Streetlight"),
    # Waste
    (["garbage", "waste", "trash", "rubbish", "litter", "dumped",
      "overflowing", "dead animal", "smell", "stink", "stench"], "Waste"),
    # Noise
    (["noise", "loud", "music", "midnight", "sound pollution",
      "honking", "blaring", "decibel"], "Noise"),
    # Heritage Damage
    (["heritage", "monument", "historical", "ancient", "archaeological",
      "heritage street"], "Heritage Damage"),
    # Heat Hazard
    (["heat", "sunstroke", "heatwave", "heat wave", "scorching",
      "temperature", "burning pavement"], "Heat Hazard"),
    # Road Damage (after Pothole so potholes don't fall here)
    (["road damage", "road surface", "cracked road", "sinking road",
      "road crack", "broken road", "cracked and sinking",
      "footpath", "tiles broken", "upturned"], "Road Damage"),
]


def _match_category(description: str) -> str:
    """Return the best-matching category from description text."""
    desc_lower = description.lower()
    for keywords, category in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                return category
    return "Other"


def _match_priority(description: str) -> str:
    """Return Urgent if any severity keyword is present, else Standard."""
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """Build a reason sentence citing words from the description."""
    desc_lower = description.lower()

    # Find which category keywords matched
    cat_evidence = []
    for keywords, cat in CATEGORY_RULES:
        if cat == category:
            for kw in keywords:
                if kw in desc_lower:
                    cat_evidence.append(kw)
            break

    # Find which severity keywords matched
    sev_evidence = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    parts = []
    if cat_evidence:
        parts.append(f"description mentions '{cat_evidence[0]}'")
    else:
        parts.append(f"description does not clearly match a specific category")

    if sev_evidence:
        parts.append(f"severity keyword '{sev_evidence[0]}' triggers Urgent priority")
    else:
        parts.append(f"no severity keywords found so priority is {priority}")

    return "Classified because " + "; ".join(parts) + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # Handle missing / empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    category = _match_category(description)
    priority = _match_priority(description)
    reason = _build_reason(description, category, priority)

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never skips rows. Never crashes on bad rows.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception:
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": "Classification failed for this row.",
                "flag": "NEEDS_REVIEW"
            }
        results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
