"""
UC-0A — Complaint Classifier
Classifies civic complaints by category and priority using rule-based keyword matching.
Implements agents.md enforcement rules and skills.md skill definitions.
"""
import argparse
import csv
import re
import sys

# Allowed categories — exact strings only
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword mappings — order matters (more specific first)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "pot-hole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogging", "waterlogged", "submerged", "knee-deep", "knee deep"],
    "Streetlight": ["streetlight", "street light", "street-light", "lights out", "light out", "lamp post", "lamppost", "flickering"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dumped", "overflowing", "litter", "dead animal", "carcass"],
    "Noise": ["noise", "loud", "music", "decibel", "honking", "blaring", "midnight"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken road", "footpath", "pavement", "tiles broken", "upturned"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "archaeological"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "temperature", "burning"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "manhole", "sewer", "gutter", "clogged"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules:
    - Category must be one of the 10 allowed values
    - Priority = Urgent if severity keywords present
    - Reason must cite specific words from description
    - Flag = NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty/null description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Determine priority based on severity keywords
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Determine category based on keyword matching
    matched_categories = []
    matched_keywords = {}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        cat_matches = [kw for kw in keywords if kw in desc_lower]
        if cat_matches:
            matched_categories.append(cat)
            matched_keywords[cat] = cat_matches

    # Determine flag and final category
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_keywords = []
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        reason_keywords = matched_keywords[category]
    else:
        # Multiple categories matched — pick the best one (first match) and flag
        category = matched_categories[0]
        reason_keywords = matched_keywords[category]
        flag = "NEEDS_REVIEW"

    # Adjust priority for minor issues without severity keywords
    if priority == "Standard" and category in ["Noise"] and not found_severity:
        priority = "Low"

    # Build reason citing specific words from description
    if found_severity and reason_keywords:
        reason = f"Description contains '{reason_keywords[0]}' (category: {category}) and severity keyword '{found_severity[0]}' triggering Urgent priority"
    elif found_severity:
        reason = f"Description contains severity keyword '{found_severity[0]}' triggering Urgent priority"
    elif reason_keywords:
        reason = f"Description contains '{reason_keywords[0]}' indicating {category}"
    else:
        reason = "No category-specific keywords found in description"

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
    Reports null rows, doesn't crash on bad rows, produces output even if some rows fail.
    """
    results = []
    total = 0
    succeeded = 0
    failed = 0

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                try:
                    result = classify_complaint(row)
                    results.append(result)
                    succeeded += 1
                except Exception as e:
                    failed += 1
                    print(f"WARNING: Row {total} failed: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    print(f"Processed: {total} | Succeeded: {succeeded} | Failed: {failed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
