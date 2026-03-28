"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Allowed categories from agents.md enforcement
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint based on description text.
    Returns: dict with keys: category, priority, reason, flag
    
    Follows enforcement rules from agents.md:
    - Category must be exactly from allowed list
    - Priority Urgent if severity keywords present
    - Reason cites specific words from description
    - Flag NEEDS_REVIEW if genuinely ambiguous (category Other)
    """
    desc_lower = description.lower()
    
    # Determine category based on keywords
    category = "Other"
    reason_word = ""
    
    if "pothole" in desc_lower:
        category = "Pothole"
        reason_word = "pothole"
    elif "flood" in desc_lower or "water" in desc_lower:
        category = "Flooding"
        reason_word = "flood" if "flood" in desc_lower else "water"
    elif "streetlight" in desc_lower or "light" in desc_lower:
        category = "Streetlight"
        reason_word = "streetlight" if "streetlight" in desc_lower else "light"
    elif "waste" in desc_lower or "garbage" in desc_lower or "trash" in desc_lower:
        category = "Waste"
        reason_word = "waste" if "waste" in desc_lower else ("garbage" if "garbage" in desc_lower else "trash")
    elif "noise" in desc_lower or "sound" in desc_lower:
        category = "Noise"
        reason_word = "noise" if "noise" in desc_lower else "sound"
    elif "road damage" in desc_lower or "crack" in desc_lower or "broken road" in desc_lower:
        category = "Road Damage"
        reason_word = "road damage" if "road damage" in desc_lower else ("crack" if "crack" in desc_lower else "broken road")
    elif "heritage" in desc_lower or "monument" in desc_lower:
        category = "Heritage Damage"
        reason_word = "heritage" if "heritage" in desc_lower else "monument"
    elif "heat" in desc_lower or "temperature" in desc_lower:
        category = "Heat Hazard"
        reason_word = "heat" if "heat" in desc_lower else "temperature"
    elif "drain" in desc_lower or "blockage" in desc_lower:
        category = "Drain Blockage"
        reason_word = "drain" if "drain" in desc_lower else "blockage"
    # If no match, category remains "Other"
    
    # Determine priority
    priority = "Standard"
    urgent_trigger = None
    for keyword in URGENT_KEYWORDS:
        if keyword in desc_lower:
            priority = "Urgent"
            urgent_trigger = keyword
            break
    
    # Build reason
    if category != "Other":
        reason = f"Classified as {category} because description contains '{reason_word}'."
    elif urgent_trigger:
        reason = f"Classified as Other due to ambiguity, but marked Urgent because description contains '{urgent_trigger}'."
    else:
        reason = "Classified as Other because no clear category keywords found in description."
    
    # Determine flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Assumes input CSV has 'description' column.
    Output CSV: category, priority, reason, flag
    Handles errors per row, writes full output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, start=1):
                description = row.get('description', '').strip()
                if not description:
                    # Empty description, treat as ambiguous
                    result = {
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Unable to classify from empty description.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    try:
                        result = classify_complaint(description)
                    except Exception as e:
                        # Log error, but continue
                        print(f"Error classifying row {row_num}: {e}")
                        result = {
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Classification failed: {str(e)}",
                            "flag": "NEEDS_REVIEW"
                        }
                results.append(result)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading input file: {e}")
    
    # Write output
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        raise RuntimeError(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    print(f"Parsed args: input={args.input}, output={args.output}")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
