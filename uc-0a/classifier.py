import argparse
import csv


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    text = row.get("description", "").lower()

    if not complaint_id or not text:
        return {
            "complaint_id": complaint_id,
            "category": "unknown",
            "priority": "low",
            "reason": "missing data",
            "flag": "yes"
        }

    category = "other"
    priority = "low"
    reason = "auto classified"

    if "flood" in text or "drain" in text or "water" in text:
        category = "water"
        priority = "high"

    elif "pothole" in text or "road" in text:
        category = "infrastructure"
        priority = "medium"

    elif "garbage" in text or "waste" in text:
        category = "sanitation"
        priority = "high"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "no"
    }


def batch_classify(input_path: str, output_path: str):

    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "unknown",
                    "priority": "low",
                    "reason": "processing error",
                    "flag": "yes"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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