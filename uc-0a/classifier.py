"""
UC-0A — Complaint Classifier
Reads a city complaint CSV and classifies each row by category, priority,
reason, and flag based strictly on the description text.

Run:
    python classifier.py \
        --input ../data/city-test-files/test_pune.csv \
        --output results_pune.csv
"""

import argparse
import csv
import sys


SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
}

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Keyword maps for category detection — checked in order, first match wins.
CATEGORY_RULES = [
    ("Pothole",        ["pothole"]),
    ("Flooding",       ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "submerged"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "blocked drain", "drain"]),
    ("Streetlight",    ["streetlight", "street light", "lights out", "flickering", "sparking"]),
    ("Waste",          ["garbage", "waste", "dump", "dumped", "animal", "dead animal", "overflowing bin"]),
    ("Noise",          ["noise", "music", "loud", "midnight"]),
    ("Road Damage",    ["road surface", "cracked", "sinking", "footpath", "tiles broken", "manhole", "tyre damage"]),
    ("Heritage Damage",["heritage"]),
    ("Heat Hazard",    ["heat", "temperature", "sun"]),
]


def detect_category(description):
    text = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return category
    return None


def detect_priority(description):
    text = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in text:
            return "Urgent"
    return "Standard"


def build_reason(description, category):
    text = description.lower()
    # Find the first severity keyword mentioned, if any
    for kw in SEVERITY_KEYWORDS:
        if kw in text:
            return f"Description mentions '{kw}' — classified as {category} with Urgent priority."
    # Otherwise cite the category-triggering keyword
    if category != "Other":
        for cat, keywords in CATEGORY_RULES:
            if cat == category:
                for kw in keywords:
                    if kw in text:
                        return f"Description mentions '{kw}' — classified as {category}."
    return f"Description does not match any specific category — classified as {category}."


def classify_complaint(row):
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description missing — cannot classify.",
            "flag":         "NEEDS_REVIEW",
        }

    category = detect_category(description)
    flag = ""

    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    priority = detect_priority(description)
    reason = build_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path, output_path):
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError as e:
        sys.exit(f"ERROR: Cannot read '{input_path}': {e}")

    if not rows:
        sys.exit(f"ERROR: No rows found in '{input_path}'.")

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category":     "Other",
                "priority":     "Low",
                "reason":       f"Processing error: {e}",
                "flag":         "NEEDS_REVIEW",
            }
        results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except OSError as e:
        sys.exit(f"ERROR: Cannot write to '{output_path}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
