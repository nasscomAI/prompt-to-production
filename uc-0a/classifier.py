"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

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
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    
    output = {
        "category": "Other",
        "priority": "Low",
        "reason": "",
        "flag": ""
    }
    
    # NEEDS_REVIEW if empty
    if not description or len(description) < 5:
        output["flag"] = "NEEDS_REVIEW"
        output["reason"] = "The input description is completely unreadable or lacks detail."
        return output

    desc_lower = description.lower()
    
    # Priority Enforcement
    urgent_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if urgent_words:
        output["priority"] = "Urgent"
        priority_reason = f"severity keyword '{urgent_words[0]}'"
    else:
        output["priority"] = "Standard"
        priority_reason = "standard processing"
        
    # Category Mapping Heuristics
    matched_category = None
    category_trigger_word = None
    
    heuristics = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "drain overflowing", "water logging"],
        "Streetlight": ["streetlight", "dark", "no light", "bulb"],
        "Waste": ["waste", "trash", "garbage", "dump"],
        "Noise": ["noise", "loud", "music", "party"],
        "Road Damage": ["road", "crack", "surface"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat hazard", "excess heat", "heatwave"],
        "Drain Blockage": ["block", "clog", "drain"]
    }
    
    for cat, keywords in heuristics.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_category = cat
                category_trigger_word = kw
                break
        if matched_category:
            break
            
    if not matched_category:
        for cat in ALLOWED_CATEGORIES:
            if cat.lower() in desc_lower and cat != "Other":
                matched_category = cat
                category_trigger_word = cat.lower()
                break

    # Formatting reasons natively
    if matched_category:
        output["category"] = matched_category
        output["reason"] = f"Classified as {matched_category} citing '{category_trigger_word}', and prioritized based on {priority_reason}."
    else:
        output["category"] = "Other"
        output["flag"] = "NEEDS_REVIEW"
        output["reason"] = "Category is genuinely ambiguous and cannot be determined from description alone."
        
    return output


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Input file '{input_path}' missing. Aborting cleanly.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"CRITICAL ERROR: Input corrupted. {e}", file=sys.stderr)
        sys.exit(1)
        
    if not fieldnames:
        print("Error: Input CSV has no headers.", file=sys.stderr)
        sys.exit(1)
        
    for new_field in ["category", "priority", "reason", "flag"]:
        if new_field not in fieldnames:
            fieldnames.append(new_field)

    processed_rows = []
    
    for row_idx, row in enumerate(rows, start=1):
        try:
            res = classify_complaint(row)
            for k in ["category", "priority", "reason", "flag"]:
                row[k] = res.get(k, "")
            processed_rows.append(row)
        except Exception as e:
            print(f"WARNING: Malformed row {row_idx} skipped. {e}")
            continue
            
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to write output file. {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
