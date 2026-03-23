"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag.
    """
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    category_keywords = {
        "Pothole": ["pothole", "tyre damage", "road surface cracked"],
        "Flooding": ["flood", "flooded", "waterlogged", "inaccessible"],
        "Streetlight": ["streetlight", "light out", "dark", "lighting"],
        "Waste": ["garbage", "waste", "overflowing bins", "bulk waste", "dumped"],
        "Noise": ["music", "noise", "loud", "sound", "past midnight"],
        "Road Damage": ["road damage", "road surface cracked", "sinkhole", "depression", "upturned"],
        "Heritage Damage": ["heritage", "heritage street", "historic"],
        "Heat Hazard": ["heat", "low shade", "hot"],
        "Drain Blockage": ["drain", "drainage", "blocked drain", "drain blocked"],
    }

    description = (row.get("description") or "").strip()
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing; could not classify.",
            "flag": "NEEDS_REVIEW",
        }

    matches = []
    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                matches.append((category, kw))
                break

    if len(matches) == 1:
        category = matches[0][0]
        matched_kw = matches[0][1]
        flag = ""
    elif len(matches) > 1:
        # Ambiguous - choose highest specific category by first encountered but mark review.
        category = matches[0][0]
        matched_kw = matches[0][1]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        matched_kw = None
        flag = "NEEDS_REVIEW"

    is_urgent = any(keyword in desc_lower for keyword in severity_keywords)
    if is_urgent:
        priority = "Urgent"
    else:
        if category in ["Noise", "Waste", "Other"]:
            priority = "Low"
        else:
            priority = "Standard"

    if matched_kw:
        reason = f"Classified as {category} based on keyword '{matched_kw}' from description."
    else:
        reason = "No category keyword found; assigned Other due to ambiguity."

    if is_urgent and "urgent" not in reason.lower():
        reason = f"Urgent due to severity keyword in description. {reason}"

    return {
        "complaint_id": complaint_id,
        "category": category if category in allowed_categories else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    input_fields = []
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []

        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    if result is None:
                        raise ValueError("classify_complaint returned None")

                    output_row = {field: result.get(field, "") for field in output_fields}
                    writer.writerow(output_row)
                except Exception as e:
                    complaint_id = (row.get("complaint_id") or "")
                    writer.writerow({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed: {str(e)}",
                        "flag": "NEEDS_REVIEW",
                    })



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
