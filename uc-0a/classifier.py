"""
UC-0A — Complaint Classifier
Implementation based on RICE framework from agents.md and skills.md.
"""
import argparse
import csv
import os

# Allowed categories - exact strings only
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implementation based on agents.md enforcement rules and skills.md specification.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()
    
    # Handle missing or empty description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    # Initialize classification result
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": ""
    }
    
    # Classify category based on keywords in description
    category_keywords = {
        "Pothole": ["pothole", "hole in road", "road hole", "crater"],
        "Flooding": ["flood", "water logging", "waterlogging", "submerged", "inundated"],
        "Streetlight": ["street light", "streetlight", "lamp", "light not working", "dark street"],
        "Waste": ["garbage", "waste", "trash", "litter", "rubbish", "dump"],
        "Noise": ["noise", "loud", "sound", "disturbance"],
        "Road Damage": ["road damage", "road crack", "broken road", "damaged road"],
        "Heritage Damage": ["heritage", "monument", "historical", "ancient"],
        "Heat Hazard": ["heat", "hot", "temperature", "heatwave"],
        "Drain Blockage": ["drain", "sewer", "blocked drain", "clogged drain", "drainage"]
    }
    
    matched_category = None
    matched_keywords = []
    
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in description:
                matched_category = category
                matched_keywords.append(keyword)
                break
        if matched_category:
            break
    
    # Set category or mark as ambiguous
    if matched_category:
        result["category"] = matched_category
        result["reason"] = f"Description contains '{matched_keywords[0]}' indicating {matched_category}."
    else:
        result["category"] = "Other"
        result["reason"] = "Unable to determine specific category from description."
        result["flag"] = "NEEDS_REVIEW"
    
    # Check for severity keywords to determine priority
    found_severity_keywords = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            found_severity_keywords.append(keyword)
    
    if found_severity_keywords:
        result["priority"] = "Urgent"
        # Update reason to mention severity
        if result["reason"] and not result["flag"]:
            result["reason"] = f"Description contains '{found_severity_keywords[0]}' indicating urgent severity; classified as {result['category']}."
        else:
            result["reason"] = f"Description contains '{found_severity_keywords[0]}' indicating urgent severity."
    else:
        # Determine Standard vs Low based on general urgency indicators
        urgency_indicators = ["immediately", "urgent", "emergency", "asap", "dangerous", "critical"]
        if any(indicator in description for indicator in urgency_indicators):
            result["priority"] = "Standard"
        else:
            result["priority"] = "Low"
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Implementation based on skills.md specification.
    Handles errors gracefully and produces output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    results = []
    error_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    error_count += 1
                    # Create error entry for failed row
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{row_num}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    print(f"Warning: Error processing row {row_num}: {e}")
    
    except Exception as e:
        raise IOError(f"Error reading input file: {e}")
    
    # Write results to output file
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            if results:
                fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
    except Exception as e:
        raise IOError(f"Error writing output file: {e}")
    
    if error_count > 0:
        print(f"Completed with {error_count} error(s). Check NEEDS_REVIEW flags in output.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
