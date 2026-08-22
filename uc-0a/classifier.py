"""
UC-0A — Complaint Classifier
Implementation using RICE enforcement and CRAFT testing loop.
"""
import argparse
import csv
import sys

CRITICAL_TRIGGERS = [
    "danger", "exposed wire", "fire", "spark", "accident",
    "injury", "injured", "hospital", "school", "child",
    "children", "contamination", "open drain", "manhole", "collapse"
]

HIGH_TRIGGERS = [
    "overflow", "blocked", "no water", "blackout",
    "pothole", "leakage", "traffic jam", "street light"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id") or row.get("id") or "UNKNOWN"
    text = (row.get("complaint_text") or row.get("description") or row.get("text") or "").strip()

    # Flag null or blank complaint descriptions
    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Unclassified",
            "priority": "LOW",
            "reason": "Missing or empty complaint text",
            "flag": "EMPTY_TEXT"
        }

    text_lower = text.lower()
    flag = "VALID"

    # Category classification
    if any(k in text_lower for k in ["garbage", "trash", "waste", "drain", "sewage", "dump", "manhole", "clean"]):
        category = "Sanitation"
    elif any(k in text_lower for k in ["pothole", "road", "traffic", "signal", "divider", "street", "footpath"]):
        category = "Roads & Traffic"
    elif any(k in text_lower for k in ["water", "pipe", "leak", "contamination", "supply", "tap"]):
        category = "Water Supply"
    elif any(k in text_lower for k in ["power", "light", "wire", "spark", "electricity", "transformer", "pole"]):
        category = "Electricity"
    else:
        category = "Public Safety"

    # Priority escalation logic (RICE Rule Enforcement)
    matched_critical = [k for k in CRITICAL_TRIGGERS if k in text_lower]
    matched_high = [k for k in HIGH_TRIGGERS if k in text_lower]

    if matched_critical:
        priority = "CRITICAL"
        reason = f"Escalated due to critical triggers: {', '.join(matched_critical)}"
        flag = "ESCALATED_SAFETY"
    elif matched_high:
        priority = "HIGH"
        reason = f"High priority triggers found: {', '.join(matched_high)}"
    else:
        priority = "MEDIUM"
        reason = "Standard routine grievance"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, handles bad rows, and produces output without crashing.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Catch malformed rows without crashing batch run
                results.append({
                    "complaint_id": row.get("complaint_id", "ERR"),
                    "category": "Error",
                    "priority": "LOW",
                    "reason": f"Row parsing failed: {str(e)}",
                    "flag": "PARSE_ERROR"
                })

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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