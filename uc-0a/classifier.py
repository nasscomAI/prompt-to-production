"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md with skills defined in skills.md.
"""
import argparse
import csv
import re
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Allowed categories
ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category keywords for classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "pit", "crater", "pavement break"],
    "Flooding": ["flood", "water", "inundation", "submerged", "waterlog"],
    "Streetlight": ["light", "streetlight", "bulb", "lamp", "dark", "lighting"],
    "Waste": ["waste", "garbage", "trash", "dump", "litter", "debris"],
    "Noise": ["noise", "sound", "loud", "music", "horn", "vibration"],
    "Road Damage": ["road", "pavement", "asphalt", "crack", "broken", "deteriorat"],
    "Heritage Damage": ["heritage", "historic", "monument", "temple", "building", "ancient"],
    "Heat Hazard": ["heat", "temperature", "warm", "scorching", "summer"],
    "Drain Blockage": ["drain", "sewer", "blockage", "clogged", "overflow", "gutter"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Input: dict with 'description' key (string, 1–500 words)
    Output: dict with keys: category, priority, reason, flag
    
    Enforcement rules from agents.md:
    - Category: exactly one of 10 allowed values or Other
    - Priority: Urgent if severity keywords present, else Standard/Low
    - Reason: one sentence citing specific complaint text
    - Flag: NEEDS_REVIEW if ambiguous, else empty string
    """
    description = row.get("description", "").strip()
    
    # Handle empty or null description
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Cannot classify empty complaint.",
            "flag": "NEEDS_REVIEW"
        }
    
    if not isinstance(description, str):
        raise ValueError(f"Description must be string, got {type(description)}")
    
    description_lower = description.lower()
    
    # Determine priority based on severity keywords
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', description_lower):
            priority = "Urgent"
            break
    
    # Determine category by keyword matching
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                matched_categories.append(category)
                break
    
    # Assign category
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"No matching category keywords found in complaint."
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        # Extract specific phrase from description for reason
        reason = f"Complaint mentions '{matched_categories[0].lower()}' with specific issue."
    else:
        # Multiple matches: ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Multiple category matches found: {', '.join(matched_categories)}."
    
    # Build reason statement with specific text citation
    if category != "Other":
        # Extract first occurrence of relevant keyword phrase
        for keyword in CATEGORY_KEYWORDS.get(category, []):
            match = re.search(r'\b\w*' + keyword + r'\w*\b', description_lower, re.IGNORECASE)
            if match:
                cited_text = description[match.start():match.end()]
                reason = f"Description contains '{cited_text}' indicating {category}."
                break
    
    if priority == "Urgent" and not flag:
        # Add severity keyword to reason if marked Urgent
        for keyword in SEVERITY_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', description_lower):
                reason = f"Complaint contains priority keyword '{keyword}': {reason}"
                break
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Input: CSV file with 'description' column
    Output: CSV with original columns + category, priority, reason, flag
    
    Error handling:
    - Missing input file: raise FileNotFoundError
    - Missing description column: raise ValueError
    - Bad rows: log warning, set category: Other and flag: NEEDS_REVIEW
    - Unwritable output: raise PermissionError (Python naturally raises this)
    """
    # Validate input file exists
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or 'description' not in reader.fieldnames:
                raise ValueError(f"Input CSV missing required 'description' column. Found: {reader.fieldnames}")
            
            rows = list(reader)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input file not found: {input_path}") from e
    
    # Classify each row
    results = []
    for idx, row in enumerate(rows):
        try:
            classification = classify_complaint(row)
            result_row = {**row, **classification}
            results.append(result_row)
        except Exception as e:
            logger.warning(f"Row {idx + 1} classification failed: {e}. Setting to Other/NEEDS_REVIEW.")
            result_row = {
                **row,
                "category": "Other",
                "priority": "Standard",
                "reason": "Classification error.",
                "flag": "NEEDS_REVIEW"
            }
            results.append(result_row)
    
    # Write results
    try:
        if results:
            fieldnames = list(results[0].keys())
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
    except PermissionError as e:
        raise PermissionError(f"Cannot write to output path: {output_path}") from e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
