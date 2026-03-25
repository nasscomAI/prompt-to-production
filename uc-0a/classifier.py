"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Priority enforcement based on severity keywords indicating urgency
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    priority = "Standard"
    matched_severity = None
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            matched_severity = kw
            break

    # Category enforcement based on allowed strictly formatted strings
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "water": "Flooding",
        "streetlight": "Streetlight",
        "lights out": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "smell": "Waste",
        "dead animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "sink": "Road Damage",
        "footpath": "Road Damage",
        "tiles": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "manhole": "Drain Blockage"
    }
    
    matched_categories = set()
    matched_kws = []
    for kw, cat in category_map.items():
        if kw in description:
            matched_categories.add(cat)
            matched_kws.append(kw)

    flag = ""
    # Enforce categorization and refuse conditions for ambiguity
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        primary_kw = matched_kws[0]
        if priority == "Urgent":
            reason = f"Classified as {category} citing '{primary_kw}', and marked Urgent due to '{matched_severity}'."
        else:
            reason = f"Classified as {category} because the description mentions '{primary_kw}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous complaint matching multiple categories: {', '.join(matched_categories)}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently determine a category from the description."

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
    results = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Explicit error handling for empty rows missing critical data
                    if not row.get("description") or not row.get("complaint_id"):
                        results.append({
                            "complaint_id": row.get("complaint_id", f"UNKNOWN_{row_num}"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Missing description or complaint ID.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                        
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ERR_{row_num}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error during processing: {str(e)}",
                        "flag": "FAILED"
                    })
    except Exception as e:
        print(f"Error reading input field: {str(e)}")
        sys.exit(1)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
