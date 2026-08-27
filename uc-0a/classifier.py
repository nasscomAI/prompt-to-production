import argparse
import csv

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


def detect_category(text):
    text = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return category
    return "Other"


def detect_priority(text):
    text = text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return priority
    return "Medium"


def classify_complaint(row):
    try:
        complaint_id = str(row.get("complaint_id", "")).strip()
        text = str(row.get("complaint_text", "")).strip()

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


def batch_classify(input_path, output_path):
    results = []

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                results.append(classify_complaint(row))
    except Exception as e:
        print("Error reading file:", e)

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
    print("Done. Results written to", args.output)
