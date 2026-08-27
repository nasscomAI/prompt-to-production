"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rules from agents.md and skills.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    
    # Handle null or empty descriptions
    if not description or str(description).lower().strip() in ["null", "none", ""]:
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Other",
            "priority": "Low",
            "reason": "Classification failed because description is missing or null.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = str(description).lower()

    # 1. Evaluate Priority (agents.md rule: "Priority must be Urgent if ANY keywords present...")
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severity = [kw for kw in severity_keywords if kw in desc_lower]
    priority = "Urgent" if found_severity else "Standard"

    # 2. Evaluate Category (agents.md rule: "Category must be exactly one of: ...")
    category_map = {
        'Pothole': ['pothole', 'crater'],
        'Flooding': ['flood', 'waterlog'],
        'Streetlight': ['streetlight', 'lights out', 'dark'],
        'Waste': ['waste', 'garbage', 'dead animal', 'dump', 'smell'],
        'Noise': ['noise', 'music'],
        'Road Damage': ['road surface', 'crack', 'footpath', 'broken'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heat'],
        'Drain Blockage': ['drain', 'manhole', 'clog', 'sewer']
    }

    category = "Other"
    flag = "NEEDS_REVIEW"
    found_cat_kw = None

    for cat, kws in category_map.items():
        for kw in kws:
            if kw in desc_lower:
                category = cat
                flag = ""
                found_cat_kw = kw
                break
        if category != "Other":
            break
            
    # agents.md rule: if category is genuinely ambiguous (Other), output flag: NEEDS_REVIEW, Priority: Low
    if category == "Other":
        flag = "NEEDS_REVIEW"
        priority = "Low"

    # 3. Construct Reason (agents.md rule: "exactly one sentence long and cites specific words")
    if category == "Other":
        reason = "Category is 'Other' because the description lacks explicit keywords mapping to the taxonomy."
    else:
        reason_parts = [f"Classified as '{category}' because the description cites '{found_cat_kw}'"]
        if priority == "Urgent":
            reason_parts.append(f"and escalated to 'Urgent' priority due to the severe keyword '{found_severity[0]}'")
        reason = " ".join(reason_parts) + "."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    # skills.md: If an individual row fails to map cleanly, mark identically as NEEDS_REVIEW...
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing crashed locally citing: {str(e)}.",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Fatal Error: Failed to open or read input dataset. Details: {e}")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Fatal Error: Failed to write to output path. Details: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Processed {args.input} and written to {args.output}")
