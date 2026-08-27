"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    # Schema rules
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    urgent_keywords = [
        "injury", "child", "school", "hospital", "ambulance",
        "fire", "hazard", "fell", "collapse"
    ]

    complaint_id = row.get("complaint_id", "")
    raw_desc = (row.get("description", "") or "").strip()
    description = raw_desc.lower()

    if not raw_desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description unavailable.",
            "flag": "NEEDS_REVIEW"
        }

    category_candidates = set()

    # Category matching prioritized by term specificity
    if "pothole" in description:
        category_candidates.add("Pothole")
    if "flood" in description or "flooded" in description:
        category_candidates.add("Flooding")
    if "drain" in description or "blocked" in description or "drainage" in description:
        category_candidates.add("Drain Blockage")
    if "streetlight" in description or "light" in description or "dark" in description:
        category_candidates.add("Streetlight")
    if "garbage" in description or "waste" in description or "dump" in description or "bin" in description:
        category_candidates.add("Waste")
    if "music" in description or "noise" in description or "loud" in description:
        category_candidates.add("Noise")
    if "heritage" in description or "heritage" in description:
        category_candidates.add("Heritage Damage")
    if "heat" in description or "hot" in description and "sun" not in description:
        category_candidates.add("Heat Hazard")
    if "manhole" in description or "road surface" in description or "crack" in description or "sink" in description:
        category_candidates.add("Road Damage")

    # Resolve category
    if len(category_candidates) == 1:
        category = next(iter(category_candidates))
        flag = ""
    elif len(category_candidates) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority rules
    priority = "Standard"
    if any(keyword in description for keyword in urgent_keywords):
        priority = "Urgent"
    elif "minor" in description or "low" in description:
        priority = "Low"

    # If category is Other when no good match, add reason accordingly
    if category == "Other":
        reason = f"Could not confidently classify: '{raw_desc}'."
    else:
        reason = f"Found {category} indicators in description: '{raw_desc}'."

    # Ensure reason is one proper sentence
    if not reason.endswith('.'):
        reason += '.'

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    with open(input_path, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        rows = []
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                complaint_id = row.get("complaint_id", "")
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Invalid row data: {str(e)}.",
                    "flag": "NEEDS_REVIEW"
                }
            rows.append(classified)

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return {"rows_processed": len(rows), "output_path": output_path}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
