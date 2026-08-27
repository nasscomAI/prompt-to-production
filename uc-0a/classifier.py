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
    desc = row.get("description", "").lower()
    
    # Severity check
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    cited_priority_word = None
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            cited_priority_word = kw
            break
            
    # Category mapping (simple rule-based proxy for AI categorization)
    category = "Other"
    cited_category_word = None
    flag = "NEEDS_REVIEW"
    
    # Check categories and find the specific citing word
    if "pothole" in desc:
        category = "Pothole"
        cited_category_word = "pothole"
        flag = ""
    elif "flood" in desc or "water" in desc and "drain" not in desc:
        category = "Flooding"
        cited_category_word = "flood" if "flood" in desc else "water"
        flag = ""
    elif "streetlight" in desc or "light" in desc:
        category = "Streetlight"
        cited_category_word = "streetlight" if "streetlight" in desc else "light"
        flag = ""
    elif "waste" in desc or "garbage" in desc or "trash" in desc:
        category = "Waste"
        cited_category_word = "waste" if "waste" in desc else ("garbage" if "garbage" in desc else "trash")
        flag = ""
    elif "noise" in desc or "loud" in desc:
        category = "Noise"
        cited_category_word = "noise" if "noise" in desc else "loud"
        flag = ""
    elif "road damage" in desc or "cracks" in desc:
        category = "Road Damage"
        cited_category_word = "road damage" if "road damage" in desc else "cracks"
        flag = ""
    elif "heritage" in desc or "monument" in desc:
        category = "Heritage Damage"
        cited_category_word = "heritage" if "heritage" in desc else "monument"
        flag = ""
    elif "heat" in desc:
        category = "Heat Hazard"
        cited_category_word = "heat"
        flag = ""
    elif "drain" in desc or "blockage" in desc:
        category = "Drain Blockage"
        cited_category_word = "drain" if "drain" in desc else "blockage"
        flag = ""

    # Formulate reason citing specific words as per agents.md
    if category == "Other":
        reason = f"Flagged as ambiguous because no clear category keywords were found in the description."
    else:
        reason_parts = [f"Classified as {category} because the description mentions '{cited_category_word}'."]
        if priority == "Urgent" and cited_priority_word:
            reason_parts.append(f"Marked Urgent due to the severity keyword '{cited_priority_word}'.")
        reason = " ".join(reason_parts)

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
    """
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during processing: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    if results:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
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
