"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic derived from agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Identify Category (Skill: identify_complaint_category)
    category_map = {
        "Pothole": ["pothole", "pit", "hole", "crater"],
        "Flooding": ["flooding", "water logging", "waterlogging", "submerged"],
        "Streetlight": ["light", "darkness", "lamp", "bulb"],
        "Waste": ["garbage", "trash", "waste", "dump", "litter"],
        "Noise": ["noise", "loud", "sound", "music", "construction"],
        "Road Damage": ["asphalt", "crack", "broken road", "dividers"],
        "Heritage Damage": ["monument", "heritage", "statue", "temple", "historical"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "shade", "water kiosk"],
        "Drain Blockage": ["drain", "sewage", "overflow", "gutter"],
    }
    
    category = "Other"
    matched_keyword = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_keyword = kw
                break
        if category != "Other":
            break

    # 2. Evaluate Priority (Skill: evaluate_severity_and_priority)
    urgent_keywords = ["injury", "child", "school", "hospital", "danger", "emergency", "accident", "safety"]
    priority = "Standard"
    severity_hit = ""
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            severity_hit = kw
            break
    
    if priority != "Urgent":
        # Check for Low priority markers
        if any(kw in description for kw in ["minor", "request", "planned"]):
            priority = "Low"

    # 3. Extract Textual Evidence (Skill: extract_textual_evidence)
    if category != "Other":
        reason = f"Classified as {category} because the description mentions '{matched_keyword}'."
        if priority == "Urgent":
            reason += f" Priority is Urgent due to '{severity_hit}'."
    else:
        reason = "Category could not be determined from the description alone."

    # 4. Refusal/Flagging logic
    flag = ""
    if not description or category == "Other":
        flag = "NEEDS_REVIEW"
        if not description:
            reason = "Empty description provided."

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
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Not crash on bad rows, produce output even if some rows fail
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Error",
                        "priority": "Error",
                        "reason": f"Processing failure: {str(e)}",
                        "flag": "FAILED"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    if not results:
        print("No data to write.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
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
