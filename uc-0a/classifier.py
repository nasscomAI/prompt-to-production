"""
UC-0A — Complaint Classifier
Classifies citizen complaints into categories and priorities based on
description text, following strict enforcement rules from agents.md.
"""
import argparse
import csv
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants from agents.md enforcement rules
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword patterns for category classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlog", "waterlogged", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp", "lighting", "dark road", "no light"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "litter", "refuse"],
    "Noise": ["noise", "drilling", "honking", "loud", "idling", "engines"],
    "Road Damage": ["road collapse", "road damage", "crater", "road crack", "road sunk",
                    "collapsed partially", "road fell"],
    "Heritage Damage": ["heritage", "monument", "historical", "archaeological"],
    "Heat Hazard": ["heat", "heatwave", "hot road", "burning surface", "heat hazard"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "drain block", "nala",
                       "stormwater drain", "mosquito breeding"],
}


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty/null descriptions
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or unintelligible",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Determine category ---
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append((category, kw))
                break

    # Resolve category
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_evidence = "no matching category keywords found"
    elif len(matched_categories) == 1:
        category = matched_categories[0][0]
        category_evidence = f"keyword '{matched_categories[0][1]}'"
    else:
        # Multiple categories matched — pick most specific, flag for review
        # Priority order: Road Damage > Pothole > Flooding > Drain Blockage > others
        priority_order = ["Road Damage", "Heritage Damage", "Heat Hazard",
                          "Pothole", "Flooding", "Drain Blockage",
                          "Streetlight", "Waste", "Noise"]
        category = "Other"
        category_evidence = ""
        for pcat in priority_order:
            for mc, kw in matched_categories:
                if mc == pcat:
                    category = mc
                    category_evidence = f"keyword '{kw}'"
                    break
            if category != "Other":
                break
        if category == "Other":
            category = matched_categories[0][0]
            category_evidence = f"keyword '{matched_categories[0][1]}'"
        flag = "NEEDS_REVIEW"

    # --- Determine priority ---
    severity_found = []
    for kw in SEVERITY_KEYWORDS:
        # Use word boundary matching for accuracy
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            severity_found.append(kw)

    if severity_found:
        priority = "Urgent"
        priority_evidence = f"severity keyword(s): {', '.join(severity_found)}"
    else:
        # Use days_open and context for Standard vs Low
        days_open = 0
        try:
            days_open = int(row.get("days_open", 0))
        except (ValueError, TypeError):
            pass

        if days_open >= 10 or any(word in desc_lower for word in
                                   ["risk", "danger", "critical", "blocked",
                                    "diverted", "struggling", "unusable"]):
            priority = "Standard"
            if days_open >= 10:
                priority_evidence = f"open {days_open} days"
            else:
                priority_evidence = "elevated concern words in description"
        else:
            priority = "Standard"
            priority_evidence = "normal complaint without severity keywords"

    # --- Build reason ---
    reason_parts = [f"Classified as {category} based on {category_evidence}"]
    reason_parts.append(f"priority {priority} due to {priority_evidence}")
    reason = "; ".join(reason_parts) + "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on bad rows — produces output even if some rows fail.
    """
    path = Path(input_path)

    if not path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Read input
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print(f"ERROR: No data rows found in {input_path}", file=sys.stderr)
        sys.exit(1)

    # Classify each row
    results = []
    urgent_count = 0
    review_count = 0

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            # Never crash mid-batch
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {str(e)}",
                "flag": "NEEDS_REVIEW",
            }

        results.append(result)
        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            review_count += 1

    # Write output CSV
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    # Report
    print(f"  Processed: {len(results)} complaints")
    print(f"  Urgent: {urgent_count}")
    print(f"  Flagged NEEDS_REVIEW: {review_count}")


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    print(f"Classifying complaints from: {args.input}")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
