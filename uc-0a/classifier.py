"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md and skills.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    if not description:
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or null.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # 1. Enforcement Rule: Severity keywords for Urgent priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    reason = "Assigned standard priority based on general complaint description."
    
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            reason = f"Description contains severity keyword: '{kw}'."
            break
            
    # 2. Enforcement Rule: Strict Category matching
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooding", "water"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "smell", "dump", "animal", "bin"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road surface", "crack", "sinking", "footpath", "tiles", "broken"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "blockage", "blocked"]
    }
    
    matches = []
    for cat, kws in category_keywords.items():
        if any(kw in desc_lower for kw in kws):
            matches.append(cat)
            
    category = "Other"
    flag = ""
    
    # 3. Enforcement Rule: Handle ambiguity with NEEDS_REVIEW
    if len(matches) == 1:
        category = matches[0]
        if priority == "Standard":
            # Find a word from the description to cite as reason
            words = description.split()
            if words:
                reason = f"Complaint mentions '{words[0]}...' related to {category.lower()}."
    elif len(matches) > 1:
        category = matches[0] # pick first match but flag it
        flag = "NEEDS_REVIEW"
        reason = "Multiple category indicators found, requires manual review."
    else:
        flag = "NEEDS_REVIEW"
        reason = "Could not confidently determine category from description alone."
        
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Resilient error handling for bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_{row_idx}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
                    
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
