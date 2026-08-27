"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = {
    "infrastructure": ["pothole", "road", "lamp", "light", "bridge", "drain", "pipe", "cable", "cobblestone", "pavement"],
    "heritage": ["heritage", "historic", "tagore", "museum", "tram", "monument", "restoration"],
    "noise": ["noise", "loud", "band", "playing", "festival", "sound", "11pm", "night"],
    "sanitation": ["garbage", "waste", "drain", "sewage", "cleaning", "dirty", "litter"],
    "traffic": ["traffic", "vehicle", "accident", "parking", "road block", "airport", "vip road"],
}

def get_category(description: str) -> str:
    desc = description.lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in desc for kw in keywords):
            return category
    return "general"

def get_priority(days_open: str, reported_by: str, description: str) -> str:
    try:
        days = int(days_open)
    except (ValueError, TypeError):
        days = 0

    desc = description.lower()
    high_keywords = ["diplomatic", "vip", "airport", "heritage", "historic", "councillor"]

    if days > 15 or any(kw in desc for kw in high_keywords) or reported_by == "Councillor Referral":
        return "HIGH"
    elif days > 7:
        return "MEDIUM"
    else:
        return "LOW"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
"""
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    days_open = row.get("days_open", "0").strip()
    reported_by = row.get("reported_by", "").strip()

    # flag nulls
    flag = ""
    if not complaint_id:
        flag = "MISSING_ID"
    elif not description:
        flag = "MISSING_DESCRIPTION"

    category = get_category(description)
    priority = get_priority(days_open, reported_by, description)
    reason = f"{category.capitalize()} issue reported via {reported_by}, open for {days_open} days."

    return {
        "complaint_id": complaint_id or "UNKNOWN",
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "error",
                    "priority": "LOW",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "ERROR",
                }
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
