import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "").strip()
    text = row.get("complaint", "").strip().lower()

    # Handle missing complaint
    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Unknown",
            "priority": "Low",
            "reason": "Empty complaint text",
            "flag": "Yes"
        }

    # Rule-based classification
    if "water" in text:
        category = "Water"
        priority = "High"
        reason = "Water-related issue"
    elif "electric" in text or "power" in text:
        category = "Electricity"
        priority = "High"
        reason = "Electricity issue"
    elif "road" in text or "pothole" in text:
        category = "Roads"
        priority = "Medium"
        reason = "Road infrastructure issue"
    elif "garbage" in text or "waste" in text:
        category = "Sanitation"
        priority = "Medium"
        reason = "Sanitation issue"
    else:
        category = "Other"
        priority = "Low"
        reason = "Unrecognized category"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "No"
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """

    results = []

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception as e:
                    result = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Error",
                        "priority": "Low",
                        "reason": str(e),
                        "flag": "Yes"
                    }
                results.append(result)

    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Write output safely
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")