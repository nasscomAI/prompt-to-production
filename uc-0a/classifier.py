"""
UC-0A — Complaint Classifier
Build using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


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
    "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or row.get("complaint_text") or "").lower()

    category = "Other"
    priority = "Low"
    reason = ""
    flag = ""

    # ---- Category classification rules ----
    if "pothole" in description:
        category = "Pothole"
        reason = "Keyword 'pothole' found"

    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"
        reason = "Keyword 'flood' or 'waterlogging' found"

    elif "streetlight" in description or "light not working" in description:
        category = "Streetlight"
        reason = "Keyword 'streetlight' found"

    elif "garbage" in description or "waste" in description or "trash" in description:
        category = "Waste"
        reason = "Keyword 'garbage' or 'waste' found"

    elif "noise" in description or "loud" in description:
        category = "Noise"
        reason = "Keyword 'noise' or 'loud' found"

    elif "road damage" in description or "crack" in description:
        category = "Road Damage"
        reason = "Keyword 'road damage' or 'crack' found"

    elif "heritage" in description or "monument" in description:
        category = "Heritage Damage"
        reason = "Keyword 'heritage' or 'monument' found"

    elif "heat" in description or "sunstroke" in description:
        category = "Heat Hazard"
        reason = "Keyword 'heat' found"

    elif "drain" in description or "sewer" in description or "block" in description:
        category = "Drain Blockage"
        reason = "Keyword 'drain' or 'blockage' found"

    else:
        category = "Other"
        reason = "No category keywords detected"
        flag = "NEEDS_REVIEW"

    # ---- Priority detection rules ----
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            reason += f"; severity keyword '{word}' detected"
            break

    if priority != "Urgent":
        priority = "Standard"

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
    Must not crash on bad rows and must still produce output.
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
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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