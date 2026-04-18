"""
UC-0A — Complaint Classifier
Mapped logically to exact RICE requirements defined inside agents.md and skills.md
No external API keys required to pass the verification step.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint (from skills.md)
    Enforces the RICE rules defined in agents.md.
    """
    desc = row.get("description", "").lower()
    comp_id = row.get("complaint_id", "")
    
    # Error Handling for null/empty rows (Skill defined: NEEDS_REVIEW fallback)
    if not desc:
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }
        
    # Enforce agents.md Rule 1: Strict Categorization (No hallucinations)
    category = "Other"
    flag = ""
    if "pothole" in desc: category = "Pothole"
    elif "flood" in desc or "water" in desc: category = "Flooding"
    elif "light" in desc or "dark" in desc: category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "trash" in desc: category = "Waste"
    elif "noise" in desc or "loud" in desc: category = "Noise"
    elif "road" in desc and "damage" in desc: category = "Road Damage"
    elif "heritage" in desc: category = "Heritage Damage"
    elif "heat" in desc: category = "Heat Hazard"
    elif "drain" in desc or "blockage" in desc: category = "Drain Blockage"
    else: 
        # Refusal Condition: Ambiguous
        flag = "NEEDS_REVIEW"

    # Enforce agents.md Rule 2: Priority assignment
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_sev = [kw for kw in severity_keywords if kw in desc]
    if found_sev:
        priority = "Urgent"

    # Enforce agents.md Rule 3: Single sentence reason citing words
    reason = f"Classified as {category} with {priority} priority."
    if found_sev:
        reason = f"Classified as {category} and elevated to Urgent priority because the description specifically cited '{found_sev[0]}'."
    elif flag == "NEEDS_REVIEW":
        reason = "Could not definitively match the description to a known taxonomy subset; flagged for review."

    return {
        "complaint_id": comp_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify (from skills.md)
    Processes CSV iteratively without crashing.
    """
    # Auto-fix pathing if the user runs it from uc-0a but provides root pathing
    if not os.path.exists(input_path) and not input_path.startswith(".."):
        alt_path = os.path.join("..", input_path)
        if os.path.exists(alt_path):
            input_path = alt_path

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Graceful error handling per skills.md
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
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
