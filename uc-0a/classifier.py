#!/usr/bin/env python3
"""
UC-0A Complaint Classifier
Classifies citizen complaints into category, priority, reason, and flag.
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
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

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "road hole", "road holes", "cavity", "depression"],
    "Flooding": ["flood", "flooding", "waterlogging", "water logging", "stagnant water", "inundation"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamp post", "street lamp", "light pole"],
    "Waste": ["garbage", "trash", "rubbish", "waste", "dump", "litter", "refuse", "debris"],
    "Noise": ["noise", "loud", "sound", "honking", "construction noise", "music", "disturbance"],
    "Road Damage": ["road damage", "cracked road", "broken road", "damaged road", "uneven road", "road repair"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "temple", "mosque", "church", "archaeological"],
    "Heat Hazard": ["heat", "temperature", "sun", "shade", "tree", "canopy", "cooling", "hot"],
    "Drain Blockage": ["drain", "drainage", "sewer", "blocked drain", "clogged", "overflow", "gutter"],
}


def classify_complaint(description: str) -> Dict[str, str]:
    """
    Classify a single complaint description.

    Args:
        description: The complaint description text.

    Returns:
        Dict with keys: category, priority, reason, flag
    """
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Determine priority based on severity keywords
    priority = "Standard"
    severity_found = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            severity_found.append(kw)
            break

    # Find matching categories
    matched_categories = []
    matched_keywords = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        found = []
        for kw in keywords:
            if kw in desc_lower:
                found.append(kw)
        if found:
            matched_categories.append(category)
            matched_keywords[category] = found

    # Determine category and flag
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"No matching category keywords found in description"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        kw = matched_keywords[category][0]
        reason = f"Classified as {category} based on keyword '{kw}' in description"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        keywords_str = ", ".join([f"'{kw}'" for cat in matched_categories for kw in matched_keywords[cat]])
        reason = f"Ambiguous: matches multiple categories ({', '.join(matched_categories)}) with keywords {keywords_str}"

    # Enhance reason with severity info if Urgent
    if priority == "Urgent" and severity_found:
        sev_str = ", ".join([f"'{kw}'" for kw in severity_found])
        reason = f"{reason}; Urgent priority due to severity keyword(s): {sev_str}"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write output CSV.

    Args:
        input_path: Path to input CSV file.
        output_path: Path to output CSV file.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no columns")

        if "description" not in reader.fieldnames:
            raise ValueError(f"Required column 'description' not found. Available columns: {reader.fieldnames}")

        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        rows = list(reader)

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            description = row.get("description", "")
            try:
                result = classify_complaint(description)
                # Validate category
                if result["category"] not in ALLOWED_CATEGORIES:
                    result["category"] = "Other"
                    result["flag"] = "NEEDS_REVIEW"
                    result["reason"] = f"Invalid category corrected to Other: {result['reason']}"
                # Validate priority
                if result["priority"] not in ALLOWED_PRIORITIES:
                    result["priority"] = "Standard"
                row.update(result)
            except Exception as e:
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = f"Classification error: {str(e)}"
                row["flag"] = "NEEDS_REVIEW"
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"Classification complete. Output written to: {args.output}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()