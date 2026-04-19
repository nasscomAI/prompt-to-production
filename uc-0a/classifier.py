"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

SEVERITY_KEYWORDS = {
    "HIGH": ["injury", "injured", "child", "children", "school", "hospital", "emergency", "accident", "death", "fatal", "risk", "danger"],
    "MEDIUM": ["pothole", "damage", "broken", "leak", "flooding", "blocked", "affected"],
    "LOW": []
}

CATEGORY_KEYWORDS = {
    "Roads": ["pothole", "road", "tyre", "vehicle", "traffic", "junction"],
    "Water": ["water", "leak", "pipe", "flooding", "drain"],
    "Sanitation": ["garbage", "waste", "sewage", "toilet", "clean"],
    "Electricity": ["light", "electric", "power", "wire", "streetlight"],
    "Other": []
}

def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").lower()
    complaint_id = row.get("complaint_id") or "UNKNOWN"
    days_open = row.get("days_open") or "0"

    # Flag nulls
    flag = "NULL_FIELDS" if not row.get("description") or not row.get("location") else "OK"

    # Category
    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in description for kw in keywords):
            category = cat
            break

    # Priority based on severity keywords + days open
    priority = "LOW"
    reason = "Standard complaint"
    for severity, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in description for kw in keywords):
            priority = severity
            matched = [kw for kw in keywords if kw in description][0]
            reason = f"Keyword match: '{matched}'"
            break

    # Escalate to HIGH if open too long
    try:
        if int(days_open) > 10 and priority == "LOW":
            priority = "MEDIUM"
            reason = f"Open for {days_open} days"
        if int(days_open) > 20:
            priority = "HIGH"
            reason = f"Critical: open for {days_open} days"
    except ValueError:
        pass

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Error",
                    "priority": "LOW",
                    "reason": str(e),
                    "flag": "ERROR"
                }
            results.append(result)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")