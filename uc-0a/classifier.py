"""
UC-0A — Complaint Classifier
Implementation based on RICE enforcement in agents.md and skills defined in skills.md.
"""
import argparse
import csv
import os

# Categories exactly as defined in README.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Priority enforcement keywords
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based heuristics 
    that match the agent's enforcement rules.
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty input description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    category = "Other"
    reason_evidence = ""
    
    if "pothole" in desc:
        category = "Pothole"
        reason_evidence = "pothole mentioned"
    elif "flood" in desc or "rain" in desc or "underpass" in desc:
        category = "Flooding"
        reason_evidence = "flooding or water accumulation mentioned"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        reason_evidence = "lighting issues or darkness reported"
    elif "garbage" in desc or "waste" in desc or "smell" in desc or "animal" in desc:
        category = "Waste"
        reason_evidence = "waste or sanitation concerns cited"
    elif "music" in desc or "noise" in desc or "loud" in desc:
        category = "Noise"
        reason_evidence = "noise disturbance reported"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        reason_evidence = "drainage or manhole issues detected"
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason_evidence = "heritage area or structure mentioned"
    elif "heat" in desc:
        category = "Heat Hazard"
        reason_evidence = "extreme heat mentioned"
    elif "cracked" in desc or "sinking" in desc or "road damage" in desc:
        category = "Road Damage"
        reason_evidence = "structural road issues reported"

    # 2. Determine Priority
    priority = "Standard"
    triggered_keyword = next((kw for kw in URGENT_KEYWORDS if kw in desc), None)
    
    if triggered_keyword:
        priority = "Urgent"
        priority_reason = f"priority escalated due to risk keyword '{triggered_keyword}'"
    else:
        # Check for Low priority cases (simple requests, no risk)
        if "music" in desc or "quiet" in desc:
            priority = "Low"
            priority_reason = "classified as minor elective concern"
        else:
            priority_reason = "classified as standard municipal duty"

    # 3. Handle Ambiguity Flag
    flag = ""
    if category == "Other" or ("safety" in desc and category == "Streetlight"):
        flag = "NEEDS_REVIEW"

    # 4. Final Reason Assembly
    # Rule: Exactly one sentence, citing specific words.
    final_reason = f"Classified as {category} with {priority} priority because the description mentions {reason_evidence} and {priority_reason}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": final_reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Processes the input CSV and writes classified results to output.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Skill error handling: include ID and flag failure
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing failure: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Critical error reading CSV: {str(e)}")
        return

    # Write Results
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    success = batch_classify(args.input, args.output)
    if success:
        print(f"Done. Results written to {args.output}")
