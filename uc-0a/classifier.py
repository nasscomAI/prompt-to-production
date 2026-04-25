"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Allowed categories from agents.md and README.md
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
    
    Enforcement rules from agents.md:
    - Category must be exactly one of the allowed list
    - Priority must be Urgent if description contains severity keywords
    - Every output row must include a reason field with one sentence citing specific words
    - If category cannot be determined, set to Other and flag to NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", row.get("id", "unknown"))
    description = row.get("description", "").lower()
    location = row.get("location", "")
    
    # Default values
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    if not description or description.strip() == "":
        flag = "NEEDS_REVIEW"
        reason = "No description provided to classify."
        return {"complaint_id": complaint_id, "category": category, "priority": priority, "reason": reason, "flag": flag}
    
    # Check for severity keywords to set Urgent priority
    description_lower = description.lower()
    has_severity_keyword = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)
    
    if has_severity_keyword:
        priority = "Urgent"
    
    # Classify category based on description keywords
    category, reason, flag = _determine_category(description, location)
    
    # Override priority if severity keyword found
    if has_severity_keyword:
        priority = "Urgent"
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _determine_category(description: str, location: str) -> tuple:
    """
    Determine the category based on description keywords.
    Returns: (category, reason, flag)
    """
    desc_lower = description.lower()
    
    # Category keyword mappings - order matters! More specific first
    category_keywords = [
        # Specific phrases first (longer matches before shorter)
        (["heritage street", "heritage", "monument", "historical", "ancient", "temple", "mosque", "church"], "Heritage Damage"),
        (["dead animal", "bulk waste", "garbage bins", "overflowing garbage"], "Waste"),
        (["waterlogging", "water logged", "standing water"], "Flooding"),
        (["manhole cover missing", "manhole", "drainage", "clogged drain", "blocked drain", "gutter blocked"], "Drain Blockage"),
        (["streetlight", "street light", "street lamp", "lights out"], "Streetlight"),
        (["pothole", "potholes", "hole in road", "road hole"], "Pothole"),
        (["flood", "flooding", "flooded", "stranded"], "Flooding"),
        (["no street light", "dark road", "light not working"], "Streetlight"),
        (["garbage", "waste", "trash", "litter", "dirty", "unclean", "swacch", "dustbin", "bin overflow"], "Waste"),
        (["noise", "loud", "disturbance", "sound", "music", "speaker", "construction noise", "past midnight"], "Noise"),
        (["road damage", "broken road", "road crack", "cracks", "uneven road", "road repair", "sinking", "surface cracked", "footpath tiles broken", "upturned"], "Road Damage"),
        (["heat", "hot", "temperature", "summer heat", "heatwave", "scorching"], "Heat Hazard"),
    ]
    
    # Check each category
    for keywords, category in category_keywords:
        for keyword in keywords:
            if keyword in desc_lower:
                reason = f"Description contains '{keyword}' indicating {category} issue."
                return category, reason, ""
    
    # If no category matched, check for ambiguity
    if len(description.strip()) < 10:
        return "Other", "Description too brief to classify accurately.", "NEEDS_REVIEW"
    
    # Default to Other with flag for ambiguous cases
    return "Other", "No specific category keywords found in description.", "NEEDS_REVIEW"


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
                    # Handle bad rows gracefully
                    complaint_id = row.get("complaint_id", row.get("id", f"row_{row_num}"))
                    errors.append(f"Row {row_num}: {str(e)}")
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading input file: {str(e)}")
    
    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Report errors if any
    if errors:
        print(f"Warning: {len(errors)} row(s) had errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
