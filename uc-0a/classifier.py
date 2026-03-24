import argparse
import csv


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Normal"
    flag = ""
    reason = ""

    if "pothole" in description:
        category = "Pothole"
        reason = "contains word pothole"
    elif "flood" in description or "water" in description:
        category = "Flooding"
        reason = "contains flooding related words"
    elif "garbage" in description or "trash" in description:
        category = "Garbage"
        reason = "contains garbage related words"
    elif "light" in description or "streetlight" in description:
        category = "Streetlight"
        reason = "contains streetlight related words"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "no clear category keywords"

    if any(word in description for word in ["urgent", "danger", "injury", "accident"]):
        priority = "High"

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

        results = []

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "ERROR",
                    "priority": "",
                    "reason": str(e),
                    "flag": "FAILED"
                })

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")