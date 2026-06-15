"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("pothole", "Pothole"),
    ("flood", "Flooding"),
    ("waterlogging", "Flooding"),
    ("submerged", "Flooding"),
    ("streetlight", "Streetlight"),
    ("light out", "Streetlight"),
    ("garbage", "Waste"),
    ("waste", "Waste"),
    ("dead animal", "Waste"),
    ("noise", "Noise"),
    ("music", "Noise"),
    ("loud music", "Noise"),
    ("road surface", "Road Damage"),
    ("road damage", "Road Damage"),
    ("cracked", "Road Damage"),
    ("sinking", "Road Damage"),
    ("heritage", "Heritage Damage"),
    ("heat", "Heat Hazard"),
    ("drain blocked", "Drain Blockage"),
    ("drainage", "Drain Blockage"),
    ("manhole", "Drain Blockage"),
]


def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")

    category = "Other"
    for keyword, cat in CATEGORY_RULES:
        if keyword in desc:
            category = cat
            break

    priority_keywords = [kw for kw in URGENT_KEYWORDS if kw in desc]
    priority = "Urgent" if priority_keywords else "Standard"

    reason_parts = []
    if category != "Other":
        reason_parts.append(f"description mentions {category.lower()}-related terms")
    else:
        reason_parts.append("description does not clearly match any known category")

    if priority_keywords:
        words = ", ".join(priority_keywords)
        reason_parts.append(f"severity keywords detected: {words}")
    else:
        reason_parts.append("no urgency keywords found")

    reason = "; ".join(reason_parts) + "."

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception as e:
                rows.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"error processing row: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
