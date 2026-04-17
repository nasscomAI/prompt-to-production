"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Built using rules defined in agents.md and skills.md.
    """
    desc = row.get("description", "").lower()
    
    # --- Category Classification ---
    assigned_category = "Other"
    ambiguous = False
    
    # Simple rule-based keyword mapping for categories
    found_categories = set()
    if "pothole" in desc:
        found_categories.add("Pothole")
    elif "crack" in desc or "road damage" in desc:
        found_categories.add("Road Damage")
        
    if "flood" in desc:
        found_categories.add("Flooding")
    if "drain" in desc:
        found_categories.add("Drain Blockage")
    if "light" in desc or "dark" in desc:
        found_categories.add("Streetlight")
    if "waste" in desc or "garbage" in desc or "trash" in desc:
        found_categories.add("Waste")
    if "noise" in desc or "loud" in desc:
        found_categories.add("Noise")
    if "heritage" in desc or "monument" in desc:
        found_categories.add("Heritage Damage")
    if "heat" in desc:
        found_categories.add("Heat Hazard")
        
    if len(found_categories) == 1:
        assigned_category = list(found_categories)[0]
    elif len(found_categories) > 1:
        # Resolve priority or treat as ambiguous
        ambiguous = True
        assigned_category = "Other"
    else:
        ambiguous = True
        assigned_category = "Other"

    # --- Priority Classification ---
    priority = "Standard"
    triggered_keywords = []
    
    for kw in URGENT_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            triggered_keywords.append(kw)
    
    # --- Ambiguity / Flag ---
    flag = "NEEDS_REVIEW" if ambiguous else ""
    
    # --- Reason generation ---
    # Must be one sentence and cite specific words
    cited_words = list(found_categories) + triggered_keywords
    if not cited_words:
        cited_words = ["unclear details"]
        
    reason = f"Classified as {assigned_category} with {priority} priority due to references to '{', '.join(cited_words)}'."
    if ambiguous:
        reason = "Classification is genuinely ambiguous, requiring manual review."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": assigned_category,
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified_result = classify_complaint(row)
                    
                    # Merge original row data with classified output
                    output_row = {**row, **classified_result}
                    results.append(output_row)
                except Exception as e:
                    # Do not crash on bad rows; log and append empty classification
                    print(f"Error classifying row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    output_row = {**row, "category": "Other", "priority": "Standard", "reason": "Failed to classify.", "flag": "NEEDS_REVIEW"}
                    results.append(output_row)
                    
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    if not results:
        print("No valid data processed. Output unaffected.")
        return
        
    # Write to output_path
    try:
        fieldnames = list(results[0].keys())
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
