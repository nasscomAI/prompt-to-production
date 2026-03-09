"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").lower().strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "missing description",
            "flag": "NEEDS_REVIEW"
        }

    # Category detection
    if any(word in description for word in ["garbage", "waste", "sewage", "trash"]):
        category = "Sanitation"
        reason = "keywords: garbage/waste/sewage"

    elif any(word in description for word in ["water", "leak", "pipeline", "tap"]):
        category = "Water"
        reason = "keywords: water/leak/pipeline"

    elif any(word in description for word in ["pothole", "road", "street", "bridge"]):
        category = "Roads"
        reason = "keywords: pothole/road/street"

    elif any(word in description for word in ["electricity", "power", "outage", "wire"]):
        category = "Electricity"
        reason = "keywords: electricity/power/outage"

    elif any(word in description for word in ["accident", "danger", "fire", "injury"]):
        category = "Public Safety"
        reason = "keywords: accident/danger/fire"

    else:
        category = "Other"
        reason = "no clear category keywords"

    # Priority detection
    if any(word in description for word in ["injury", "child", "school", "hospital", "fire", "danger"]):
        priority = "Urgent"

    elif any(word in description for word in ["leak", "outage", "pothole", "garbage"]):
        priority = "Medium"

    else:
        priority = "Low"

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
    Handles bad rows gracefully and continues processing.
    """

    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"error processing row: {e}",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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