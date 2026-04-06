"""
UC-0A — Complaint Classifier
Updated using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Priority Enforcement
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severities = [kw for kw in severity_keywords if kw in desc_lower]
    
    priority = "Urgent" if found_severities else "Standard"

    # Category Enforcement (Exact Strings Only)
    # Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    category = "Other"
    flag = "NEEDS_REVIEW"
    cited_word = ""

    # Priority mapping for categorization
    if "pothole" in desc_lower:
        category = "Pothole"
        cited_word = "pothole"
        flag = ""
    elif "flood" in desc_lower:
        category = "Flooding"
        cited_word = "flood"
        flag = ""
    elif "streetlight" in desc_lower or "lights out" in desc_lower:
        category = "Streetlight"
        cited_word = "streetlight" if "streetlight" in desc_lower else "lights out"
        flag = ""
    elif "waste" in desc_lower or "garbage" in desc_lower:
        category = "Waste"
        cited_word = "waste" if "waste" in desc_lower else "garbage"
        flag = ""
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
        cited_word = "music" if "music" in desc_lower else "noise"
        flag = ""
    elif "crack" in desc_lower or "sinking" in desc_lower or "road surface" in desc_lower:
        category = "Road Damage"
        cited_word = "crack" if "crack" in desc_lower else "road surface"
        flag = ""
    elif "heritage" in desc_lower and "damage" in desc_lower:
        category = "Heritage Damage"
        cited_word = "heritage"
        flag = ""
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        cited_word = "heat"
        flag = ""
    elif "drain" in desc_lower:
        category = "Drain Blockage"
        cited_word = "drain"
        flag = ""

    # Reason Enforcement
    if category == "Other":
        reason = "The description is genuinely ambiguous and cannot be determined from the text alone."
    else:
        if found_severities:
            reason = f"The complaint is prioritized as Urgent due to the word '{found_severities[0]}', and categorized as {category} focusing on '{cited_word}'."
        else:
            reason = f"The description primarily addresses a {category} issue, explicitly citing '{cited_word}'."

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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Apply the skills.md constraints
                    classification = classify_complaint(row)
                    
                    # Merge classification into original row, extending the dict
                    out_row = {**row, **classification}
                    results.append(out_row)
                except Exception as e:
                    # Error handling specified in skills.md
                    out_row = {**row}
                    out_row["category"] = "Other"
                    out_row["priority"] = "Low"
                    out_row["reason"] = f"Row parsing failed: {e}"
                    out_row["flag"] = "NEEDS_REVIEW"
                    results.append(out_row)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return

    if not results:
        print("No data extracted. Aborting CSV generation.")
        return

    out_keys = ["complaint_id", "date_raised", "city", "ward", "location", "description", "reported_by", "days_open", "category", "priority", "reason", "flag"]
    # Ensure keys in results that aren't in out_keys don't get lost
    actual_keys = list(results[0].keys())
    ordered_keys = out_keys + [k for k in actual_keys if k not in out_keys]
    ordered_keys = [k for k in ordered_keys if k in actual_keys]
    
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=ordered_keys)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to '{output_path}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
