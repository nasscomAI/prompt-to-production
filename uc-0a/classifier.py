"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Allowed categories (exact strings only)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces rules from agents.md:
    - Category must be exactly one of allowed values
    - Priority must be Urgent if severity keywords present
    - Reason must cite specific words from description
    - Flag NEEDS_REVIEW if category is ambiguous
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()
    location = row.get("location", "")
    reported_by = row.get("reported_by", "")
    
    # Determine category based on description keywords
    category = "Other"
    flag = ""
    
    # Category mapping based on keywords in description
    if any(word in description for word in ["pothole", "pot hole"]):
        category = "Pothole"
    elif any(word in description for word in ["flood", "flooded", "stranded", "inaccessible"]):
        category = "Flooding"
    elif any(word in description for word in ["streetlight", "street light", "lights out", "lighting", "flickering"]):
        category = "Streetlight"
    elif any(word in description for word in ["garbage", "waste", "dumped", "bin", "overflowing"]):
        category = "Waste"
    elif any(word in description for word in ["noise", "music", "past midnight", "loud"]):
        category = "Noise"
    elif any(word in description for word in ["road surface", "cracked", "sinking", "surface damaged", "manhole", "footpath", "tiles", "cover"]):
        category = "Road Damage"
    elif any(word in description for word in ["heritage", "heritage street"]):
        category = "Heritage Damage"
    elif any(word in description for word in ["heat", "heat hazard", "temperature"]):
        category = "Heat Hazard"
    elif any(word in description for word in ["drain", "drainage", "drain blocked"]):
        category = "Drain Blockage"
    else:
        # Ambiguous - flag for review
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    # Determine priority based on severity keywords
    priority = "Standard"
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    
    # Generate reason citing specific words from description
    # Extract key phrase from description
    desc_original = row.get("description", "")
    # Use first few words of description as reason basis
    words = desc_original.split()
    reason = "Classified based on: " + " ".join(words[:8]) + ("..." if len(words) > 8 else "")
    
    return {
        "complaint_id": complaint_id,
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
    errors = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    # Still add a row with error info
                    results.append({
                        "complaint_id": row.get("complaint_id", f"UNKNOWN-{row_num}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return
    
    # Write output CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {str(e)}")
        return
    
    # Report errors
    if errors:
        print(f"Warning: {len(errors)} row(s) had errors:")
        for err in errors:
            print(f"  - {err}")
    
    print(f"Processed {len(results)} complaints. Output written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
