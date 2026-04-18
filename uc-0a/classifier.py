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
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Priority enforcement
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_keywords = [kw for kw in severity_keywords if kw in desc_lower]
    
    if found_keywords:
        priority = "Urgent"
        kw_used = found_keywords[0]
        priority_reason = f"contains severity keyword '{kw_used}'"
    else:
        priority = "Standard"
        priority_reason = "does not contain severity keywords"

    # Category classification based on agents.md
    if "pothole" in desc_lower:
        category = "Pothole"
        cat_reason = "mentions 'pothole'"
    elif "flood" in desc_lower or "water" in desc_lower:
        category = "Flooding"
        cat_reason = "mentions 'flood'"
    elif "light" in desc_lower or "dark" in desc_lower:
        category = "Streetlight"
        cat_reason = "mentions 'light' or 'dark'"
    elif "waste" in desc_lower or "garbage" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
        cat_reason = "mentions waste or garbage"
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
        cat_reason = "mentions noise or music"
    elif "crack" in desc_lower or "tiles broken" in desc_lower:
        category = "Road Damage"
        cat_reason = "mentions road damage indicators"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        cat_reason = "mentions 'heritage'"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        cat_reason = "mentions 'heat'"
    elif "drain" in desc_lower or "manhole" in desc_lower:
        category = "Drain Blockage"
        cat_reason = "mentions 'drain' or 'manhole'"
    else:
        category = "Other"
        cat_reason = "has no obvious category matches"

    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = f"Set to NEEDS_REVIEW because it {cat_reason}; Priority is {priority} because description {priority_reason}."
    else:
        flag = ""
        reason = f"Classified as {category} because description {cat_reason}; Priority is {priority} because description {priority_reason}."

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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    # Add the new fields if they don't exist
    new_fields = ["category", "priority", "reason", "flag"]
    if fieldnames is None:
        fieldnames = []
    
    for f in new_fields:
        if f not in fieldnames:
            fieldnames.append(f)

    for row in rows:
        try:
            if not row.get("description"):
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = "Description is missing."
                row["flag"] = "NEEDS_REVIEW"
                continue

            classification = classify_complaint(row)
            for key in new_fields:
                row[key] = classification.get(key, "")
        except Exception as e:
            row["category"] = "Other"
            row["priority"] = "Low"
            row["reason"] = f"Processing error: {str(e)}"
            row["flag"] = "NEEDS_REVIEW"

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
