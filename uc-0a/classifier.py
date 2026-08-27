import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Normal"
    reason = ""
    flag = ""

    if "pothole" in description:
        category = "Pothole"
        reason = "Detected keyword pothole"

    elif "flood" in description or "water logging" in description:
        category = "Flooding"
        reason = "Detected flooding related keyword"

    elif "garbage" in description or "trash" in description:
        category = "Garbage"
        reason = "Detected garbage related keyword"

    elif "water supply" in description or "no water" in description:
        category = "Water Supply"
        reason = "Detected water supply issue"

    else:
        category = "Other"
        reason = "No clear keyword found"
        flag = "NEEDS_REVIEW"

    urgent_words = ["injury", "child", "school", "hospital"]

    for word in urgent_words:
        if word in description:
            priority = "Urgent"
            reason += f"; urgent keyword: {word}"
            break

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        with open(output_path, "w", newline='', encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception:
                    writer.writerow({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Normal",
                        "reason": "Error processing complaint",
                        "flag": "NEEDS_REVIEW"
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")