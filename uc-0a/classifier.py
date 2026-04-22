
"""
UC-0A — Complaint Classifier

Built using README.md constraints + agents.md + skills.md
Deterministic, rule-based implementation (no hallucination).
"""

import argparse
import csv
import sys

# --------------------------------------------------
# UC-0A Constants (MUST match README exactly)
# --------------------------------------------------

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


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def contains_severity_keyword(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in SEVERITY_KEYWORDS)


def assign_category(text: str) -> tuple[str, str]:
    """
    Returns (category, flag)
    Flag is NEEDS_REVIEW only when genuinely ambiguous.
    """
    t = text.lower()

    matched = []

    if "pothole" in t:
        matched.append("Pothole")

    if "flood" in t or "waterlogging" in t:
        matched.append("Flooding")

    if "streetlight" in t or "lamp" in t or "light not working" in t:
        matched.append("Streetlight")

    if "garbage" in t or "waste" in t or "trash" in t:
        matched.append("Waste")

    if "noise" in t or "loud" in t:
        matched.append("Noise")

    if "road" in t and "damage" in t:
        matched.append("Road Damage")

    if "heritage" in t or "monument" in t:
        matched.append("Heritage Damage")

    if "heat" in t or "heatwave" in t:
        matched.append("Heat Hazard")

    if "drain" in t or "sewage" in t or "blocked" in t:
        matched.append("Drain Blockage")

    if len(matched) == 1:
        return matched[0], ""

    if len(matched) > 1:
        return matched[0], "NEEDS_REVIEW"

    return "Other", ""


# --------------------------------------------------
# Core Skill: classify_complaint
# --------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns dict with keys:
    complaint_id, category, priority, reason, flag
    """

    try:
        complaint_id = row.get("complaint_id", "").strip()
        description = row.get("description", "").strip()

        if not description:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": "Description is missing or empty.",
                "flag": "NEEDS_REVIEW",
            }

        category, flag = assign_category(description)

        if contains_severity_keyword(description):
            priority = "Urgent"
            reason = (
                "Marked Urgent due to severity keyword present in description such as "
                f"'{next(w for w in SEVERITY_KEYWORDS if w in description.lower())}'."
            )
        else:
            priority = "Standard"
            reason = "Classified based on complaint description text."

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": f"Classification failed due to error: {str(e)}",
            "flag": "NEEDS_REVIEW",
        }


# --------------------------------------------------
# Core Skill: batch_classify
# --------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must not crash on bad rows.
    """

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            result = classify_complaint(row)
            writer.writerow(result)


# --------------------------------------------------
# CLI entrypoint
# --------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument(
        "--input",
        required=True,
        help="./data/city-test-files/test_bangalore.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="./results_bangalore.csv",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
