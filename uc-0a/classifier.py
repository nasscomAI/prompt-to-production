"""
UC-0A: Civic Complaint Classifier
Classifies complaints from a CSV file into category, priority, reason, and flag.
Uses keyword matching on the description field.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import sys
from collections import OrderedDict

# Category keywords — order matters for tie-breaking (first match wins)
CATEGORY_KEYWORDS = OrderedDict([
    ("Pothole", ["pothole", "tyre damage", "tire damage"]),
    ("Flooding", ["flood", "waterlogging", "waterlogged", "submerged", "knee-deep", "stranded"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "dark", "flickering", "sparking"]),
    ("Waste", ["garbage", "waste", "litter", "overflowing bins", "dump", "rubbish", "dead animal"]),
    ("Noise", ["noise", "loud music", "music past midnight", "honking"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "broken", "footpath", "tiles broken", "upturned"]),
    ("Heritage Damage", ["heritage", "monument", "historical"]),
    ("Heat Hazard", ["heat", "temperature", "sunstroke"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "manhole", "manhole cover"]),
])

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(description, days_open):
    """
    Classify a single complaint based on its description and days_open.

    Returns a dict with keys: category, priority, reason, flag.
    """
    desc_lower = description.lower()

    # Step 1: Find all matching categories and the keywords that matched
    matched_categories = []
    matched_keywords_by_category = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        found_keywords = [kw for kw in keywords if kw in desc_lower]
        if found_keywords:
            matched_categories.append(category)
            matched_keywords_by_category[category] = found_keywords

    # Step 2: Determine category (first match wins) or Other
    if matched_categories:
        category = matched_categories[0]
    else:
        category = "Other"

    # Step 3: Determine flag
    flag = "NEEDS_REVIEW" if len(matched_categories) >= 2 else ""

    # Step 4: Determine priority
    severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    try:
        days = int(days_open)
    except (ValueError, TypeError):
        days = 0

    if severity_found or days > 15:
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # Step 5: Build reason
    if category != "Other":
        keywords_cited = matched_keywords_by_category[category]
        reason_parts = []
        reason_parts.append(f'Contains "{keywords_cited[0]}" indicating {category}')
        if severity_found:
            reason_parts.append(f'marked urgent due to "{severity_found[0]}"')
        elif days > 15:
            reason_parts.append(f"marked urgent due to {days} days open")
        reason = "; ".join(reason_parts) + "."
    else:
        reason = "No clear category keywords matched in the description."
        if severity_found:
            reason = f'No clear category keywords matched; marked urgent due to "{severity_found[0]}".'
        elif days > 15:
            reason = f"No clear category keywords matched; marked urgent due to {days} days open."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    """
    Read complaints from input CSV, classify each, write results to output CSV.
    """
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            complaint_id = row["complaint_id"]
            description = row.get("description", "")
            days_open = row.get("days_open", "0")

            classification = classify_complaint(description, days_open)
            results.append({
                "complaint_id": complaint_id,
                "category": classification["category"],
                "priority": classification["priority"],
                "reason": classification["reason"],
                "flag": classification["flag"],
            })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    total = len(results)
    categories = {}
    urgent_count = 0
    review_count = 0
    for r in results:
        categories[r["category"]] = categories.get(r["category"], 0) + 1
        if r["priority"] == "Urgent":
            urgent_count += 1
        if r["flag"] == "NEEDS_REVIEW":
            review_count += 1

    print(f"Classified {total} complaints → {output_path}")
    print(f"  Urgent: {urgent_count}")
    print(f"  Needs Review: {review_count}")
    print("  Categories:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0A Civic Complaint Classifier"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to input CSV file (e.g., ../data/city-test-files/test_pune.csv)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to output CSV file (e.g., results_pune.csv)"
    )
    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
