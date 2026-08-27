import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_text = row.get("complaint", "").lower()

    # Default values
    category = "Other"
    priority = "LOW"
    reason = ""
    flag = "OK"

    if not complaint_text:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Unknown",
            "priority": "LOW",
            "reason": "Empty complaint",
            "flag": "NULL"
        }

    # Category detection
    if any(word in complaint_text for word in ["garbage", "waste"]):
        category = "Sanitation"
    elif any(word in complaint_text for word in ["water", "leak"]):
        category = "Water"
    elif any(word in complaint_text for word in ["road", "pothole"]):
        category = "Road"
    elif any(word in complaint_text for word in ["electricity", "power"]):
        category = "Electricity"

    # Priority detection (RICE enforcement)
    if any(word in complaint_text for word in ["hospital", "school", "child", "injury"]):
        priority = "HIGH"
        reason = "Sensitive location or risk"
    elif any(word in complaint_text for word in ["urgent", "immediate"]):
        priority = "HIGH"
        reason = "Urgency detected"
    elif any(word in complaint_text for word in ["delay", "late"]):
        priority = "MEDIUM"
        reason = "Service delay"
    else:
        priority = "LOW"
        reason = "General issue"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    try:
        with open(input_path, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Error",
                        "priority": "LOW",
                        "reason": str(e),
                        "flag": "FAILED"
                    })
    except Exception as e:
        print("Error reading input file:", e)
        return

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
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