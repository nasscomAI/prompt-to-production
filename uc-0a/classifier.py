import argparse
import csv


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Normal"
    reason = ""
    flag = ""

    if not description:
        flag = "Missing description"
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description",
            "flag": flag
        }

    if "garbage" in description or "trash" in description:
        category = "Sanitation"
        reason = "Detected garbage keyword"

    elif "water" in description:
        category = "Water"
        reason = "Detected water keyword"

    elif "pothole" in description or "road" in description:
        category = "Roads"
        reason = "Detected road keyword"

    elif "electricity" in description or "power" in description:
        category = "Electricity"
        reason = "Detected electricity keyword"

    if "injury" in description or "child" in description or "school" in description:
        priority = "Urgent"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):

    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing row",
                    "flag": str(e)
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
