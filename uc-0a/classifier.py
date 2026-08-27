import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    try:
        complaint_id = row.get("complaint_id", "").strip()
        text = row.get("complaint", "").lower().strip()

        # 🚨 Handle null / empty
        if not text:
            return {
                "complaint_id": complaint_id,
                "category": "unknown",
                "priority": "low",
                "reason": "empty complaint",
                "flag": "null"
            }

        # 🟢 CATEGORY RULES
        if any(word in text for word in ["garbage", "waste", "trash"]):
            category = "sanitation"
        elif any(word in text for word in ["water", "leak", "pipeline"]):
            category = "water"
        elif any(word in text for word in ["road", "pothole", "street"]):
            category = "infrastructure"
        elif any(word in text for word in ["electricity", "power", "light"]):
            category = "electricity"
        else:
            category = "other"

        # 🔴 PRIORITY RULES (RICE-style severity)
        if any(word in text for word in ["hospital", "injury", "accident", "fire"]):
            priority = "high"
        elif any(word in text for word in ["school", "public", "urgent"]):
            priority = "medium"
        else:
            priority = "low"

        # 🧠 REASON
        reason = f"Detected category={category}, priority={priority}"

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": "ok"
        }

    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "error",
            "priority": "low",
            "reason": str(e),
            "flag": "error"
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: not crash, handle bad rows, always produce output.
    """

    results = []

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                result = classify_complaint(row)
                results.append(result)

    except Exception as e:
        print("Error reading input file:", e)

    # Always write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for r in results:
            writer.writerow(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
