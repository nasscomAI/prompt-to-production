"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on context and enforcement rules in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # Priority enforcement logic
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description:
            priority = "Urgent"
            break
            
    # Category taxonomy and logic
    categories = {
        "Pothole": ["pothole", "crater", "sinkhole"],
        "Flooding": ["flood", "waterlogging", "underwater", "submerge"],
        "Streetlight": ["streetlight", "bulb", "dark", "no light"],
        "Waste": ["waste", "garbage", "trash", "dump", "litter"],
        "Noise": ["noise", "loud", "sound", "music"],
        "Road Damage": ["road", "crack", "asphalt", "pavement"],
        "Heritage Damage": ["heritage", "statue", "monument", "historic"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "thermal"],
        "Drain Blockage": ["drain", "sewage", "clog", "overflow"],
    }
    
    category = "Other"
    flag = ""
    reason = "No specific category keywords found."
    
    assigned_categories = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                assigned_categories.append((cat, kw))
                break # move to next category
                
    if len(assigned_categories) == 1:
        category, matched_kw = assigned_categories[0]
        reason = f"Identified as {category} because description mentions '{matched_kw}'."
    elif len(assigned_categories) > 1:
        # Ambiguous case: multiple matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        found_kw = ", ".join([kw for cat, kw in assigned_categories])
        reason = f"Ambiguous complaint matching multiple categories: {found_kw}."
    else:
        # No matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not determine category from description alone."

    # Priority reason override if Urgent
    if priority == "Urgent":
        matched_severity = [kw for kw in severity_keywords if kw in description]
        reason += f" Priority set to Urgent due to: {', '.join(matched_severity)}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results to output CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            results = []
            
            for row in reader:
                # Handle nulls or missing fields as specified in skills.md
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "MISSING"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Don't crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if not results:
            print("No data processed.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Error during batch classification: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

