"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row enforcing the agents.md and skills.md rules programmatically.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Pre-defined Enforcement mappings
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # 1. Category Classification based on matching keywords
    category = "Other"
    cited_words = []
    
    if "pothole" in desc:
        category, cited_words = "Pothole", ["pothole"]
    elif "flood" in desc or "water" in desc:
        category, cited_words = "Flooding", ["flood", "water"]
    elif "light" in desc or "dark" in desc:
        category, cited_words = "Streetlight", ["light", "dark"]
    elif "waste" in desc or "garbage" in desc or "animal" in desc or "smell" in desc:
        category, cited_words = "Waste", ["waste", "garbage", "animal", "smell"]
    elif "noise" in desc or "music" in desc:
        category, cited_words = "Noise", ["noise", "music"]
    elif "road" in desc or "crack" in desc or "path" in desc:
        category, cited_words = "Road Damage", ["road", "crack", "path"]
    elif "heritage" in desc:
        category, cited_words = "Heritage Damage", ["heritage"]
    elif "heat" in desc:
        category, cited_words = "Heat Hazard", ["heat"]
    elif "drain" in desc or "manhole" in desc:
        category, cited_words = "Drain Blockage", ["drain", "manhole"]
        
    # 2. Priority Classification based on severity
    priority = "Standard"
    found_sev_keywords = [kw for kw in severity_keywords if kw in desc]
    
    if found_sev_keywords:
        priority = "Urgent"
    
    # 3. Generating a verifiable Reason sentence
    matched_words = [kw for kw in cited_words if kw in desc]
    if priority == "Urgent":
        reason = f"Classified with Urgent priority because the description mentions '{', '.join(found_sev_keywords)}'."
    elif category != "Other":
        reason = f"Assigned Standard priority and category {category} since the issue mentions '{matched_words[0]}'."
    else:
        reason = "Unable to map this description to a defined category."

    # 4. Evaluating ambiguity Flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
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
    Safely process rows without crashing on failures.
    """
    classified_rows = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    # Merge classification fields back to the original row
                    row["category"] = result["category"]
                    row["priority"] = result["priority"]
                    row["reason"] = result["reason"]
                    row["flag"] = result["flag"]
                    classified_rows.append(row)
                except Exception as row_error:
                    print(f"Skipped row {row.get('complaint_id', 'UNKNOWN')} due to error: {row_error}")

        if not classified_rows:
            print("No classified rows to write. Output file not created.")
            return

        # Prepare fieldnames for output, preserving original + appending new keys
        output_fields = list(fieldnames)
        for expected_key in ["category", "priority", "reason", "flag"]:
            if expected_key not in output_fields:
                output_fields.append(expected_key)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as out_f:
            writer = csv.DictWriter(out_f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(classified_rows)
            
    except Exception as e:
        print(f"Failed to process batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
