import argparse
import csv

# Simple keyword-based rules
CATEGORY_KEYWORDS = {
    "Water": ["water", "leak", "pipe", "supply"],
    "Electricity": ["electric", "power", "outage", "voltage"],
    "Sanitation": ["garbage", "waste", "clean", "drain", "sewage"],
    "Road": ["road", "pothole", "traffic", "street"],
}

PRIORITY_KEYWORDS = {
    "High": ["urgent", "immediately", "emergency", "danger"],
    "Medium": ["soon", "delay", "issue"],
    "Low": ["request", "minor", "normal"]
}


def detect_category(text: str) -> str:
    text = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return category
    return "Other"


def detect_priority(text: str) -> str:
    text = text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return priority
    return "Medium"


def classify_complaint(row: dict) -> dict:
    try:
        complaint_id = row.get("complaint_id", "").strip()
        text = row.get("complaint_text", "").strip()

        # Handle missing values
        if not complaint_id or not text:
            return {
                "complaint_id": complaint_id or "UNKNOWN",
                "category": "Unknown",
                "priority": "Low",
                "reason": "Missing complaint_id or complaint_text",
                "flag": "YES"
            }

        category = detect_category(text)
        priority = detect_priority(text)

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": "Keyword-based classification",
            "flag": "NO"
        }

    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Error",
            "priority": "Low",
            "reason": str(e),
            "flag": "YES"
        }


def batch_classify(input_path: str, output_path: str):
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                result = classify_complaint(row)
                results.append(result)

    except Exception as e:
        print(f"Error reading input file: {e}")

    # Always write output
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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
