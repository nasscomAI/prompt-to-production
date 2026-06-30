"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = row.get("description", "").lower()
    category = "Other"
    priority = "Standard"
    reason = "Could not determine category."
    flag = "NEEDS_REVIEW"
    if "pothole" in description:
        category = "Pothole"
        reason = "Detected the word 'pothole'."
        flag = ""
    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"
        reason = "Detected flooding-related words."
        flag = ""

    elif "streetlight" in description or "street light" in description:
        category = "Streetlight"
        reason = "Detected streetlight-related words."
        flag = ""

    elif "garbage" in description or "waste" in description or "trash" in description:
        category = "Waste"
        reason = "Detected waste-related words."
        flag = ""

    elif "noise" in description or "loud" in description:
        category = "Noise"
        reason = "Detected noise-related words."
        flag = ""

    elif "road damage" in description or "crack" in description:
        category = "Road Damage"
        reason = "Detected road damage."
        flag = ""

    elif "heritage" in description or "monument" in description:
        category = "Heritage Damage"
        reason = "Detected heritage-related words."
        flag = ""

    elif "heat" in description:
        category = "Heat Hazard"
        reason = "Detected heat-related words."
        flag = ""

    elif "drain" in description or "drainage" in description:
        category = "Drain Blockage"
        reason = "Detected drain-related words."
        flag = ""
    urgent_keywords = [
        "injury",
        "child",
        "school",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse"
    ]

    if any(word in description for word in urgent_keywords):
        priority = "Urgent"
    return {
        "complaint_id": row.get("complaint_id", ""),
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
    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        results = []
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Error processing complaint.",
                    "flag": "NEEDS_REVIEW",
                })
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
