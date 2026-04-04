"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md and skills.md.
"""
import argparse
import csv
import logging
import re
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Enforce allowed categories from agents.md
ALLOWED_CATEGORIES = [
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
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category keywords for classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "pit", "broken pavement", "asphalt"],
    "Flooding": ["flood", "water", "waterlogged", "stagnant", "submersion"],
    "Streetlight": ["streetlight", "street light", "light", "lamppost", "dark"],
    "Waste": ["waste", "garbage", "litter", "trash", "dumping", "refuse"],
    "Noise": ["noise", "sound", "loud", "disturbance", "honking", "blaring"],
    "Road Damage": ["road damage", "crack", "rut", "uneven road", "broken road"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "structure"],
    "Heat Hazard": ["heat", "temperature", "hot", "extreme heat", "scorching"],
    "Drain Blockage": ["drain", "blocked", "blockage", "overflow", "clogged"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using RICE enforcement rules.
    Returns: dict with keys: category, priority, reason, flag
    
    Enforces:
    - Category must be exactly one of 10 allowed values
    - Priority Urgent if severity keywords present, else Standard
    - Reason must cite specific words from description
    - Flag NEEDS_REVIEW if category is Other (ambiguous)
    """
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    
    # Rule 2: Determine priority based on severity keywords
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', desc_lower):
            priority = "Urgent"
            break
    
    # Rule 1: Classify category based on keyword matching
    category = "Other"
    best_match_keyword = ""
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', desc_lower):
                category = cat
                best_match_keyword = keyword
                break
        if category != "Other":
            break
    
    # Rule 3: Generate reason sentence citing specific words from description
    if best_match_keyword:
        reason = f"Description contains '{best_match_keyword}' indicating {category}."
    elif priority == "Urgent":
        for keyword in SEVERITY_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', desc_lower):
                reason = f"Marked as {priority} due to '{keyword}' keyword."
                break
    else:
        reason = "Unable to classify from description provided."
    
    # Rule 4: Set flag for ambiguous/low-confidence classifications
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
    Preserves original columns. Logs errors but continues processing.
    """
    rows = []
    
    # Read input CSV
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        raise
    
    if not rows:
        logger.warning(f"No rows found in {input_path}")
        return
    
    # Classify each row
    output_rows = []
    for idx, row in enumerate(rows, start=2):  # start=2 accounts for header
        try:
            if not row.get("description"):
                logger.warning(f"Row {idx}: missing description, skipping")
                continue
            
            classification = classify_complaint(row)
            output_row = {**row, **classification}
            output_rows.append(output_row)
        except Exception as e:
            logger.warning(f"Row {idx}: error during classification: {e}")
            continue
    
    # Write output CSV
    try:
        if output_rows:
            fieldnames = list(output_rows[0].keys())
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(output_rows)
        else:
            logger.warning("No valid rows to write to output file")
    except Exception as e:
        logger.error(f"Error writing output file {output_path}: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
