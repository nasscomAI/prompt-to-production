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
    """
    description = row.get("description", "").lower()
    
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = "Could not confidently determine category from description."

    # Priority Check: Urgent if description contains specific severity keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(kw in description for kw in urgent_keywords):
        priority = "Urgent"
    
    # Category Check (Heuristics based on keyword matching)
    if "pothole" in description:
        category = "Pothole"
        reason = "Contains word 'pothole'."
    elif "flood" in description:
        category = "Flooding"
        reason = "Contains word 'flood'."
    elif "streetlight" in description or "lights out" in description:
        category = "Streetlight"
        reason = "Contains 'streetlight' or 'lights out'."
    elif "garbage" in description or "waste" in description or "dead animal" in description:
        category = "Waste"
        reason = "Contains words related to waste or animal."
    elif "music" in description or "noise" in description:
        category = "Noise"
        reason = "Contains 'music' or 'noise'."
    elif "cracked" in description or "sinking" in description or "broken" in description or "upturned" in description:
        category = "Road Damage"
        reason = "Contains words indicating road damage."
    elif "drain" in description or "manhole" in description:
        category = "Drain Blockage"
        reason = "Contains 'drain' or 'manhole'."
    elif "heritage" in description:
        category = "Heritage Damage"
        reason = "Contains word 'heritage'."
    elif "heat" in description:
        category = "Heat Hazard"
        reason = "Contains word 'heat'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.DictReader(fin)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                res = classify_complaint(row)
                writer.writerow(res)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
