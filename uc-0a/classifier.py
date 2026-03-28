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
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # --- Enforcement Rule 2: Priority ---
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_keywords = [kw for kw in severity_keywords if kw in desc]
    
    if found_keywords:
        priority = "Urgent"
        priority_reason = f"severity keyword '{found_keywords[0]}' detected"
    else:
        priority = "Standard"
        priority_reason = "no severity keywords detected"
        
    # --- Enforcement Rule 1 & 4: Category and Flag ---
    category = "Other"
    flag = "NEEDS_REVIEW"
    matched_reason = "the description lacks clear categorization"
    
    if "pothole" in desc:
        category, flag, matched_reason = "Pothole", "", "mentions pothole"
    elif "flood" in desc or "rain" in desc:
        if "drain" in desc and "block" in desc:
            category, flag, matched_reason = "Drain Blockage", "", "mentions blocked drain"
        else:
            category, flag, matched_reason = "Flooding", "", "mentions flooding or rain"
    elif "light" in desc or "dark" in desc:
        if "heritage" in desc:
            category, flag, matched_reason = "Heritage Damage", "NEEDS_REVIEW", "mentions heritage and lights"
        else:
            category, flag, matched_reason = "Streetlight", "", "mentions lights or darkness"
    elif "garbage" in desc or "waste" in desc or "animal" in desc:
        category, flag, matched_reason = "Waste", "", "mentions garbage, waste, or animal"
    elif "music" in desc or "noise" in desc:
        category, flag, matched_reason = "Noise", "", "mentions music or noise"
    elif "road" in desc or "crack" in desc or "manhole" in desc or "footpath" in desc or "tiles" in desc:
        category, flag, matched_reason = "Road Damage", "", "mentions road, crack, footpath, or tiles"
    elif "heat" in desc:
        category, flag, matched_reason = "Heat Hazard", "", "mentions heat"
    elif "drain" in desc and "block" in desc:
        category, flag, matched_reason = "Drain Blockage", "", "mentions drain block"
    elif "heritage" in desc:
        category, flag, matched_reason = "Heritage Damage", "NEEDS_REVIEW", "mentions heritage"

    # --- Enforcement Rule 3: Single sentence reason ---
    reason = f"The issue is classified as {category} because it {matched_reason}, and priority is {priority} because {priority_reason}."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print("Error: Input CSV file is empty or malformed.", file=sys.stderr)
                sys.exit(1)
            
            rows = list(reader)
            fieldnames = list(reader.fieldnames)
    except Exception as e:
        print(f"Error reading input CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure output schemas exist in fieldnames
    new_fields = ["category", "priority", "reason", "flag"]
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    classified_rows = []
    for idx, row in enumerate(rows):
        try:
            classification = classify_complaint(row)
            # Update row with new fields
            for field in new_fields:
                row[field] = classification.get(field, "")
            classified_rows.append(row)
        except Exception as e:
            # Error handling for invalid/ambiguous inputs (does not crash the batch process)
            print(f"Error classifying row {idx + 1}: {e}. Skipping.", file=sys.stderr)
            continue

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
    except Exception as e:
        print(f"Error writing output CSV: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
