"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# Allowed categories and severity keywords as defined in agents.md and README.md
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    # Normalize description for matching
    desc_lower = description.lower()
    
    # Simple rule-based classification based on keywords in description (as an AI stand-in/fallback for now, or direct implementation if no API is provided)
    # For a real AI agent, we would structure an LLM prompt here.
    # Since I cannot run an external LLM natively here without an API key, I will build a robust rule-based logic that strictly adheres to `agents.md` enforcement rules to satisfy the RICE requirements.

    # 1. Determine Category
    category = "Other"
    matching_category_words = []
    
    if "pothole" in desc_lower:
        category = "Pothole"
        matching_category_words.append("pothole")
    elif "flood" in desc_lower or "water" in desc_lower:
        category = "Flooding"
        matching_category_words.append("flood/water")
    elif "light" in desc_lower or "street light" in desc_lower:
        category = "Streetlight"
        matching_category_words.append("light")
    elif "trash" in desc_lower or "waste" in desc_lower or "garbage" in desc_lower:
        category = "Waste"
        matching_category_words.append("waste/trash")
    elif "noise" in desc_lower or "loud" in desc_lower or "music" in desc_lower:
        category = "Noise"
        matching_category_words.append("noise/loud")
    elif ("road" in desc_lower and "damage" in desc_lower) or "crack" in desc_lower:
        category = "Road Damage"
        matching_category_words.append("road damage/crack")
    elif "heritage" in desc_lower or "monument" in desc_lower:
        category = "Heritage Damage"
        matching_category_words.append("heritage/monument")
    elif "heat" in desc_lower or "hot" in desc_lower:
        category = "Heat Hazard"
        matching_category_words.append("heat")
    elif "drain" in desc_lower or "block" in desc_lower or "sewage" in desc_lower:
        category = "Drain Blockage"
        matching_category_words.append("drain/blockage")

    # Flag for ambiguity (If we couldn't match a specific category)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    priority = "Standard"
    matching_severity_words = []
    
    for word in SEVERITY_KEYWORDS:
        if re.search(rf'\b{word}\b', desc_lower):
            priority = "Urgent"
            matching_severity_words.append(word)

    # 3. Generate Reason
    reason_parts = []
    if matching_category_words:
        reason_parts.append(f"Category '{category}' selected due to mention of '{', '.join(matching_category_words)}'.")
    else:
        reason_parts.append("Category 'Other' selected as description is ambiguous.")
        
    if matching_severity_words:
        reason_parts.append(f"Priority '{priority}' assigned due to severity keywords: '{', '.join(matching_severity_words)}'.")
    else:
        reason_parts.append(f"Priority '{priority}' assigned as no severity keywords were found.")
        
    reason = " ".join(reason_parts)

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
    """
    results = []
    
    # Read input CSV
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Do not crash on bad rows, produce output even if some rows fail
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}", file=sys.stderr)
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error parsing input: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
         print(f"Error reading input file: {e}", file=sys.stderr)
         sys.exit(1)

    # Write output CSV
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
