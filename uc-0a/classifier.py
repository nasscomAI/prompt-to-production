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
    text = row.get("description", "").lower()
    
    # Check priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in text]
    
    if found_urgent:
        priority = "Urgent"
        reason = f"Contains severity keyword: '{found_urgent[0]}'."
    else:
        priority = "Standard"
        reason = "No severity keywords detected."

    # Determine category
    category = "Other"
    flag = ""
    
    # Simple heuristics for classification
    categories_found = []
    if "pothole" in text:
        categories_found.append("Pothole")
    if "flood" in text:
        categories_found.append("Flooding")
    if "streetlight" in text or "lights out" in text:
        categories_found.append("Streetlight")
    if "garbage" in text or "waste" in text or "dead animal" in text:
        categories_found.append("Waste")
    if "music" in text or "noise" in text:
        categories_found.append("Noise")
    if "crack" in text or "sinking" in text or "broken" in text:
        categories_found.append("Road Damage")
    if "heritage" in text:
        categories_found.append("Heritage Damage")
    if "heat" in text:
        categories_found.append("Heat Hazard")
    if "drain" in text:
        categories_found.append("Drain Blockage")

    if len(categories_found) == 1:
        category = categories_found[0]
    elif len(categories_found) > 1:
        category = categories_found[0]
        flag = "NEEDS_REVIEW"
        reason += f" Ambiguous categories: {', '.join(categories_found)}."
    elif "manhole cover missing" in text:
        category = "Other" # Handled explicitly to not flag anything else
        
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
                    if not row.get("complaint_id") or not row.get("description"):
                        results.append({
                            "complaint_id": row.get("complaint_id", "UNKNOWN"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Null or missing data",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                    
                    classification = classify_complaint(row)
                    
                    # Merge classification results into row or just save classification
                    # Requirement says: category and priority_flag columns are stripped - you must classify them
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    if not results:
        print("No results to write.")
        return

    fieldnames = list(results[0].keys())
    # Ensure classification fields are in the output if not already
    for field in ["complaint_id", "category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
