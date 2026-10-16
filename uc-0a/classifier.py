"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Strict Taxonomy from enforcement rules
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Strict Severity Keywords from enforcement rules
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row implementing strict RICE rules.
    Expects 'description' key in row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    
    # Target structure initialization
    result = {
        "category": "Other",
        "priority": "Standard",
        "reason": "Default classification due to lack of descriptive identifiers.",
        "flag": ""
    }
    
    # 1. Guardrail against empty or null descriptions
    if not description:
        result["reason"] = "Empty or null description provided."
        result["flag"] = "NEEDS_REVIEW"
        return result

    desc_lower = description.lower()

    # 2. SEVERITY BLINDNESS ENFORCEMENT
    # Scan for exact keyword triggers to force Urgent priority
    triggered_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if triggered_keywords:
        result["priority"] = "Urgent"
        
    # 3. TAXONOMY DRIFT & AMBIGUITY ENFORCEMENT
    # Simple rule-based mapping for demo/deterministic fallback. 
    # If extending to an LLM, parse its output against ALLOWED_CATEGORIES.
    matched_categories = []
    if "pot hole" in desc_lower or "pothole" in desc_lower:
        matched_categories.append("Pothole")
    if "flood" in desc_lower or "waterlogging" in desc_lower:
        matched_categories.append("Flooding")
    if "light" in desc_lower or "dark" in desc_lower:
        matched_categories.append("Streetlight")
    if "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower:
        matched_categories.append("Waste")
    if "noise" in desc_lower or "loud" in desc_lower or "sound" in desc_lower:
        matched_categories.append("Noise")
    if "crack" in desc_lower or "road structural" in desc_lower:
        matched_categories.append("Road Damage")
    if "monument" in desc_lower or "heritage" in desc_lower:
        matched_categories.append("Heritage Damage")
    if "heat" in desc_lower or "wave" in desc_lower or "hot" in desc_lower:
        matched_categories.append("Heat Hazard")
    if "drain" in desc_lower or "sewer" in desc_lower:
        matched_categories.append("Drain Blockage")

    # Handle Ambiguity & Assign Category
    if len(matched_categories) == 1:
        result["category"] = matched_categories[0]
    elif len(matched_categories) > 1:
        # False Confidence Guardrail: Too many matches means ambiguity
        result["category"] = matched_categories[0] # Pick primary
        result["flag"] = "NEEDS_REVIEW"
    else:
        # No concrete category matches
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    # 4. MISSING JUSTIFICATION ENFORCEMENT
    # Build exactly one sentence citing specific words wrapped in quotes
    if triggered_keywords and result["category"] != "Other":
        result["reason"] = f"Classified as {result['category']} with Urgent priority due to the presence of safety keyword '{triggered_keywords[0]}'."
    elif result["flag"] == "NEEDS_REVIEW":
        result["reason"] = "Flagged for human review because text context is highly ambiguous or lacks single taxonomy matches."
    else:
        result["reason"] = f"Identified context relating to {result['category'].lower()} directly from citizen description."

    # Final sanity validation against valid taxonomy
    if result["category"] not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Ensures program doesn't crash on bad rows or missing directories.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    rows_processed = 0
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames if reader.fieldnames else []
        
        # Ensure our required output headers are added without duplicate clashes
        output_fields = list(fieldnames)
        for field in ["category", "priority", "reason", "flag"]:
            if field not in output_fields:
                output_fields.append(field)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()

            for row_idx, row in enumerate(reader, start=1):
                try:
                    # Execute individual classification
                    classification = classify_complaint(row)
                    
                    # Merge results directly into row data
                    row.update(classification)
                    writer.writerow(row)
                    rows_processed += 1
                    
                except Exception as e:
                    # Guardrail against complete script crashes
                    print(f"Warning: Skipping corrupted/malformed data on row {row_idx}: {e}")
                    continue

    print(f"Successfully processed {rows_processed} entries.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")