"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md and skills from skills.md.
"""
import argparse
import csv
import re
from typing import Dict

# Enforcement: Exact category strings - no variations allowed
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Enforcement: Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

# Category detection patterns - prioritized by severity
CATEGORY_PATTERNS = [
    ("Heritage Damage", [r"\bheritage\b", r"\bmonument\b", r"\bhistoric\b", r"\barchaeological\b"]),
    ("Heat Hazard", [r"\bheat\b", r"\bheatwave\b", r"\bhot\b.*hazard", r"\btemperature\b.*extreme"]),
    ("Flooding", [r"\bflood", r"\bwater.*log", r"\binundat", r"\bsubmerg"]),
    ("Drain Blockage", [r"\bdrain", r"\bsewer", r"\bmanhole", r"\bclog"]),
    ("Pothole", [r"\bpothole", r"\bcrater", r"\bhole\b.*road"]),
    ("Road Damage", [r"\broad\b.*damag", r"\bpavement\b.*crack", r"\basphalt\b.*break", r"\bcrack.*road"]),
    ("Streetlight", [r"\bstreet.*light", r"\bstreet.*lamp", r"\blamp.*post", r"\blight.*pole"]),
    ("Waste", [r"\bwaste\b", r"\bgarbage\b", r"\btrash\b", r"\brubbish\b", r"\blitter"]),
    ("Noise", [r"\bnoise\b", r"\bloud\b", r"\bsound\b.*disturb"]),
]


def classify_complaint(description: str) -> Dict[str, str]:
    """
    Classify a single complaint by category, priority, and provide justification.
    
    Args:
        description: String containing the complaint description text
        
    Returns:
        Dictionary with keys: category, priority, reason, flag
        
    Enforcement rules from agents.md:
    1. Category must be exactly one from ALLOWED_CATEGORIES
    2. Priority is Urgent if severity keywords present, otherwise Standard/Low
    3. Reason must cite specific words from description
    4. Flag is NEEDS_REVIEW when category is ambiguous
    """
    # Error handling: empty or null input
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Check for severity keywords to determine Urgent priority
    found_severity_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
    is_urgent = len(found_severity_keywords) > 0
    
    # Detect category using pattern matching
    matched_categories = []
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, description_lower):
                matched_categories.append(category)
                break
    
    # Determine final category and flag
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No clear category indicators found in description"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        # Extract specific words that led to classification
        reason = f"Description contains '{category.lower()}' related terms"
    else:
        # Multiple categories match - use most severe but flag for review
        category = matched_categories[0]  # First match (prioritized by severity)
        flag = "NEEDS_REVIEW"
        reason = f"Multiple categories apply: {', '.join(matched_categories[:2])}"
    
    # Determine priority with reason citation
    if is_urgent:
        priority = "Urgent"
        if reason and flag != "NEEDS_REVIEW":
            reason = f"Contains severity keyword(s): {', '.join(found_severity_keywords[:2])}. " + reason
        elif flag != "NEEDS_REVIEW":
            reason = f"Contains severity keyword(s): {', '.join(found_severity_keywords[:2])}"
    else:
        # Use Standard as default, Low for minor issues
        minor_indicators = ["broken", "not working", "needs repair"]
        if any(indicator in description_lower for indicator in minor_indicators) and not is_urgent:
            priority = "Standard"
        else:
            priority = "Standard"
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Args:
        input_path: Path to input CSV with columns: id, description
        output_path: Path to write output CSV
        
    Error handling:
    - Raises clear error if input file missing or malformed
    - Logs row ID and continues processing if any row fails
    - Writes partial results with error summary at end
    """
    errors = []
    processed_count = 0
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate required columns
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                raise ValueError(f"Input file missing required 'description' column. Found columns: {reader.fieldnames}")
            
            # Determine ID column name (could be 'id', 'complaint_id', etc.)
            id_column = None
            for possible_id in ['id', 'complaint_id', 'ID']:
                if possible_id in reader.fieldnames:
                    id_column = possible_id
                    break
            
            if not id_column:
                raise ValueError(f"Input file missing ID column. Found columns: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    complaint_id = row.get(id_column, f"row_{row_num}")
                    description = row.get('description', '')
                    
                    # Classify the complaint
                    classification = classify_complaint(description)
                    
                    # Build result row
                    result = {
                        'id': complaint_id,
                        'description': description,
                        'category': classification['category'],
                        'priority': classification['priority'],
                        'reason': classification['reason'],
                        'flag': classification['flag']
                    }
                    results.append(result)
                    processed_count += 1
                    
                except Exception as e:
                    error_msg = f"Row {row_num} (ID: {row.get(id_column, 'unknown')}): {str(e)}"
                    errors.append(error_msg)
                    print(f"Warning: {error_msg}")
                    # Continue processing other rows
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading input file {input_path}: {str(e)}")
    
    # Write results to output CSV
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'description', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        raise Exception(f"Error writing output file {output_path}: {str(e)}")
    
    # Print summary
    print(f"Processed {processed_count} complaints")
    if errors:
        print(f"Encountered {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
