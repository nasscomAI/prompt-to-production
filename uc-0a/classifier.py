"""
UC-0A — Complaint Classifier
Implements RICE framework from agents.md and skills from skills.md
"""

import argparse
import csv
import os
from typing import Dict

# Exact allowed categories - no variations
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

# Severity keywords that must trigger Urgent
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

# Category keywords mapping (description keywords → category)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "potholed"],
    "Flooding": [
        "flood",
        "flooding",
        "flooded",
        "water logging",
        "waterlogging",
        "water stagnation",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "streetlights",
        "street lights",
        "lamp post",
        "lampost",
    ],
    "Waste": ["garbage", "trash", "waste", "debris", "dumping", "litter"],
    "Noise": ["noise", "noisy", "sound", "loud", "horn", "honking"],
    "Road Damage": ["road damage", "damaged road", "broken road"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient"],
    "Heat Hazard": ["heat", "temperature", "hot", "heatwave", "sunstroke"],
    "Drain Blockage": ["drain", "clogged", "sewer", "manhole", "gutter", "sewage"],
}


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """
    Classifies a single citizen complaint row into category, priority, reason, and flag fields.
    """
    description = row.get("description", "").strip()

    # Error handling: empty/missing description
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # Check for severity keywords
    has_severity = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)

    # Determine category based on keyword matching
    category_scores = {}
    matched_keywords = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                category_scores[category] = category_scores.get(category, 0) + 1
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)

    # Determine final category
    if len(category_scores) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Description contains no recognizable category keywords"
    elif len(category_scores) == 1:
        category = list(category_scores.keys())[0]
        flag = ""
        best_keyword = matched_keywords[0] if matched_keywords else "complaint"
        reason = f"Description contains '{best_keyword}' indicating {category}."
    else:
        sorted_scores = sorted(
            category_scores.items(), key=lambda x: x[1], reverse=True
        )
        if sorted_scores[0][1] > sorted_scores[1][1]:
            category = sorted_scores[0][0]
            flag = ""
            best_keyword = matched_keywords[0] if matched_keywords else "keywords"
            reason = f"Description contains '{best_keyword}' indicating {category}."
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = f"Description matches multiple categories: {', '.join(category_scores.keys())}"

    # Determine priority
    if has_severity:
        priority = "Urgent"
        severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
        if severity_found:
            reason = f"Description contains '{severity_found[0]}' requiring urgent attention. {reason}"
    else:
        if category in [
            "Pothole",
            "Road Damage",
            "Drain Blockage",
            "Flooding",
            "Heat Hazard",
        ]:
            priority = "Standard"
        else:
            priority = "Low"

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV file, applies classify_complaint to each row, and writes results to an output CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    input_rows = []
    fieldnames = []

    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            input_rows = list(reader)
    except csv.Error as e:
        raise FileNotFoundError(f"Invalid CSV file: {input_path} - {e}")

    output_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]

    if len(input_rows) == 0:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
        return

    output_rows = []
    for row in input_rows:
        try:
            classification = classify_complaint(row)

            if not all(
                key in classification
                for key in ["category", "priority", "reason", "flag"]
            ):
                raise ValueError("Invalid classification output")

            if classification["category"] not in ALLOWED_CATEGORIES:
                classification["category"] = "Other"
                classification["flag"] = "NEEDS_REVIEW"
                classification["reason"] = (
                    "Invalid category generated, defaulted to Other"
                )

            output_row = {**row, **classification}
            output_rows.append(output_row)

        except Exception as e:
            print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
            output_row = {
                **row,
                "category": "Other",
                "priority": "Low",
                "reason": f"Processing error: {str(e)}",
                "flag": "NEEDS_REVIEW",
            }
            output_rows.append(output_row)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
