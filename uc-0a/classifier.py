import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    try:
        text = str(row.get("description", "")).lower()

        if not text or text.strip() == "":
            return {
                "complaint_id": row.get("complaint_id"),
                "category": "Unknown",
                "priority": "Low",
                "reason": "Empty description",
                "flag": "YES"
            }

       
        if "water" in text:
            category = "Water"
            priority = "High"
        elif "road" in text or "pothole" in text:
            category = "Road"
            priority = "Medium"
        elif "garbage" in text or "waste" in text:
            category = "Sanitation"
            priority = "High"
        elif "electric" in text or "light" in text:
            category = "Electricity"
            priority = "Medium"
        else:
            category = "Other"
            priority = "Low"

        return {
            "complaint_id": row.get("complaint_id"),
            "category": category,
            "priority": priority,
            "reason": f"Detected keywords in description: {text[:30]}",
            "flag": "NO"
        }

    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id"),
            "category": "Error",
            "priority": "Low",
            "reason": str(e),
            "flag": "YES"
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []

    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id"),
                "category": "Error",
                "priority": "Low",
                "reason": str(e),
                "flag": "YES"
            })

    # Write output
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
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
