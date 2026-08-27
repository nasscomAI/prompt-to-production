"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Allowed categories (from agents.md enforcement rule 1)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords (from agents.md enforcement rule 2)
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Category keywords for classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "crater", "gap in road"],
    "Flooding": ["flood", "flooding", "waterlogged", "water accumulation", "standing water"],
    "Streetlight": ["streetlight", "street light", "lamp", "light not working", "dark"],
    "Waste": ["waste", "garbage", "trash", "litter", "dustbin", "bin"],
    "Noise": ["noise", "sound", "loud", "music", "construction noise"],
    "Road Damage": ["road damage", "broken road", "road broken", "road crack"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "structure"],
    "Heat Hazard": ["heat", "hot", "temperature", "heatwave", "sun"],
    "Drain Blockage": ["drain", "drainage", "clogged", "blocked drain", "sewage"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implementation follows agents.md enforcement rules:
    1. Category must be exactly one of allowed list
    2. Priority = Urgent if severity keywords present
    3. Reason must cite specific words from description
    4. Ambiguous cases → Other + NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", row.get("id", ""))
    description = row.get("description", "").lower()
    
    if not description or description.strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient information",
            "flag": "NEEDS_REVIEW"
        }
    
    # Determine category
    category = "Other"
    matched_keywords = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                category = cat
                matched_keywords.append(kw)
                break
        if category != "Other":
            break
    
    # Check if ambiguous - no clear category match
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""
    
    # Determine priority (enforcement rule 2)
    priority = "Standard"
    severity_found = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            severity_found.append(keyword)
            break
    
    # Build reason citing specific words (enforcement rule 3)
    if severity_found:
        reason = f"Contains severity keyword: {severity_found[0]}"
    elif matched_keywords:
        reason = f"Contains category keyword: {matched_keywords[0]}"
    else:
        reason = "No specific keywords found in description"
        flag = "NEEDS_REVIEW" if not flag else flag
    
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
    
    Implementation follows skills.md:
    - flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Handle bad rows gracefully
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{row_num}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {str(e)}")
    
    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
