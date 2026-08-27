"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").lower().strip()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    urgent_keywords = [
        "injury",
        "child",
        "school",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse"
    ]

    # Category detection
    if "pothole" in description:
        category = "Pothole"
        reason = 'Contains the keyword "pothole".'

    elif "garbage" in description or "waste" in description:
        category = "Waste"
        reason = 'Contains the keyword "garbage" or "waste".'

    elif "flood" in description or "flooded" in description:
        category = "Flooding"
        reason = 'Contains the keyword "flood".'

    elif "drain" in description:
        category = "Drain Blockage"
        reason = 'Contains the keyword "drain".'

    elif "streetlight" in description or "light" in description:
        category = "Streetlight"
        reason = 'Contains the keyword "streetlight" or "light".'

    elif "noise" in description:
        category = "Noise"
        reason = 'Contains the keyword "noise".'

    elif "heritage" in description:
        category = "Heritage Damage"
        reason = 'Contains the keyword "heritage".'

    elif "heat" in description:
        category = "Heat Hazard"
        reason = 'Contains the keyword "heat".'

    elif "road" in description:
        category = "Road Damage"
        reason = 'Contains the keyword "road".'

    # Priority detection
    if any(word in description for word in urgent_keywords):
        priority = "Urgent"

    # Flag handling
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "No strong keyword match found; requires manual review."

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
    Must handle bad rows safely and continue processing.
    """

    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # skip completely empty rows safely
                if not row:
                    continue

                result = classify_complaint(row)
                results.append(result)

            except Exception:
                # never crash entire program
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Error processing row; default fallback applied.",
                    "flag": "NEEDS_REVIEW"
                })

    # write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
