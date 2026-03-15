"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv
import re


# Allowed categories from agents.md
CATEGORIES = [
    "Pothole",
    "Flooding",
    "Garbage",
    "Streetlight",
    "Water Leakage",
    "Road Damage",
    "Drainage Blockage",
]

PRIORITY_LEVELS = ["Low", "Medium", "High", "Urgent"]


def preprocess_text(text: str) -> str:
    """Clean and normalize complaint text."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_category(text: str):
    """Determine complaint category."""
    if any(k in text for k in ["pothole", "hole in road"]):
        return "Pothole"
    if any(k in text for k in ["flood", "flooding", "water on road"]):
        return "Flooding"
    if any(k in text for k in ["garbage", "trash", "waste", "dump"]):
        return "Garbage"
    if any(k in text for k in ["streetlight", "street light", "lamp", "light not working"]):
        return "Streetlight"
    if any(k in text for k in ["water leak", "pipe leak", "water leakage"]):
        return "Water Leakage"
    if any(k in text for k in ["road broken", "road damage", "damaged road"]):
        return "Road Damage"
    if any(k in text for k in ["drain", "drainage", "blocked drain"]):
        return "Drainage Blockage"

    return "Other"


def detect_priority(text: str):
    """Determine complaint priority."""
    urgent_keywords = ["injury", "accident", "child", "school", "exposed wire", "severe flooding"]
    high_keywords = ["danger", "blocked road", "overflow", "large pothole"]

    if any(k in text for k in urgent_keywords):
        return "Urgent"

    if any(k in text for k in high_keywords):
        return "High"

    if len(text) > 0:
        return "Medium"

    return "Low"


def extract_reason(original_text: str, category: str):
    """Generate reason referencing complaint text."""
    words = original_text.split()
    snippet = " ".join(words[:8])
    return f"Detected '{category}' from description snippet: '{snippet}'"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing",
            "flag": "NULL_DESCRIPTION",
        }

    try:
        clean_text = preprocess_text(description)

        category = detect_category(clean_text)
        priority = detect_priority(clean_text)

        reason = extract_reason(description, category)

        flag = ""
        if category == "Other":
            flag = "NEEDS_REVIEW"

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    except Exception as e:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": f"Processing error: {str(e)}",
            "flag": "ERROR",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing failed: {str(e)}",
                    "flag": "ROW_ERROR",
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")