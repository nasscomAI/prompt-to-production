"""
UC-0A — Complaint Classifier
Build using RICE → agents.md → skills.md → CRAFT workflow
"""

import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dictionary with:
    complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Normal"
    reason = ""
    flag = ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Category rules
    if "water" in description or "leak" in description or "pipeline" in description:
        category = "Water"
        reason = "Detected keyword: water/leak/pipeline"

    elif "pothole" in description or "road" in description:
        category = "Roads"
        reason = "Detected keyword: pothole/road"

    elif "power" in description or "electric" in description:
        category = "Electricity"
        reason = "Detected keyword: power/electric"

    elif "garbage" in description or "waste" in description or "trash" in description:
        category = "Sanitation"
        reason = "Detected keyword: garbage/waste"

    else:
        category = "Other"
        reason = "No category keyword found"
        flag = "NEEDS_REVIEW"

    # Priority rules
    if "injury" in description or "child" in description or "school" in description or "hospital" in description:
        priority = "Urgent"
    elif "danger" in description or "blocked" in description:
        priority = "High"
    else:
        priority = "Normal"

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
    Must not crash on bad rows.
    """

    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
