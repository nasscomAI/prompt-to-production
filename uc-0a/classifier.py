"""
UC-0A — Complaint Classifier
Implementation based on RICE framework (agents.md) and skills definition (skills.md).
"""
import argparse
import csv
import os

# Configuration from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row using rules from agents.md.
    In a production setting, this would typically involve an LLM call.
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # 1. Determine Priority (Enforcement Rule: Urgent if severity keywords present)
    priority = "Standard"
    found_severity_kw = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if found_severity_kw:
        priority = "Urgent"
    
    # 2. Determine Category (Enforcement Rule: Must be exactly from ALLOWED_CATEGORIES)
    # Simple heuristic-based classification for this implementation
    category = "Other"
    reason_fragment = "general issue"
    
    if "pothole" in desc_lower:
        category = "Pothole"
        reason_fragment = "pothole"
    elif "flood" in desc_lower or "underpass" in desc_lower:
        category = "Flooding"
        reason_fragment = "flooding"
    elif "light" in desc_lower:
        category = "Streetlight"
        reason_fragment = "streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower:
        category = "Waste"
        reason_fragment = "waste/garbage"
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
        reason_fragment = "noise"
    elif "drain" in desc_lower:
        category = "Drain Blockage"
        reason_fragment = "drain blockage"
    elif "road" in desc_lower and "damage" in desc_lower:
        category = "Road Damage"
        reason_fragment = "road damage"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        reason_fragment = "heritage"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        reason_fragment = "heat"

    # 3. Generate Reason (Enforcement Rule: One sentence citing specific words)
    kw_citation = found_severity_kw[0] if found_severity_kw else reason_fragment
    reason = f"Classified as {category} with {priority} priority because the description mentions '{kw_citation}'."

    # 4. Handle Ambiguity (Enforcement Rule: flag NEEDS_REVIEW if category is Other)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write to output CSV.
    Handles missing files and malformed rows as per skills.md.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Row {row_idx}: Failed to classify. Error: {e}")
                    # Continue processing other rows
    except Exception as e:
        print(f"Critical error reading input file: {e}")
        return

    if not results:
        print("No results to write.")
        return

    try:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    print(f"Starting batch classification: {args.input} -> {args.output}")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

