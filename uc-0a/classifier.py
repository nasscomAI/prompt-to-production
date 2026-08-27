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
    description = row.get("description", "").lower()
    
    # Priority Keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Category Keywords mapping
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "loud": "Noise",
        "road damage": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    category = "Other"
    reason_cat = "Could not determine category from description."
    flag = "NEEDS_REVIEW"
    
    # Determine category
    found_categories = []
    for kw, cat in category_map.items():
        if kw in description:
            found_categories.append((kw, cat))
    
    if found_categories:
        # Use first matched category
        match_kw, category = found_categories[0]
        reason_cat = f"Categorized as '{category}' due to keyword '{match_kw}'."
        flag = ""
        
    # Determine priority
    priority = "Standard"
    reason_pri = "No severity keywords found."
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            reason_pri = f"Priority upgraded to Urgent due to severity keyword '{kw}'."
            break
            
    reason = f"{reason_cat} {reason_pri}"
    
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    # Not crashing on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN",
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
