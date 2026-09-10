import argparse
import csv


CATEGORIES = [
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

URGENT_KEYWORDS = [
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


def classify_complaint(row: dict) -> dict:
    description = str(row.get("description", "") or "").strip()
    complaint_id = row.get("complaint_id", "")

    text = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "waterlogging" in text:
        category = "Flooding"
    elif "streetlight" in text or "street light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text or "trash" in text:
        category = "Waste"
    elif "noise" in text or "loud" in text:
        category = "Noise"
    elif "road damage" in text or "damaged road" in text or "road surface" in text or ("road" in text and "cracked" in text):
        category = "Road Damage"
    elif "heritage" in text or "monument" in text:
        category = "Heritage Damage"
    elif "heat" in text or "hot" in text:
        category = "Heat Hazard"
    elif "drain" in text or "blocked drain" in text:
        category = "Drain Blockage"
    else:
        category = "Other"

    priority = (
        "Urgent"
        if any(keyword in text for keyword in URGENT_KEYWORDS)
        else "Standard"
    )

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    reason = f"The complaint mentions: {description}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Could not safely classify this row: {exc}.",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    args = parser.parse_args()

    batch_classify(args.input_path, args.output_path)
