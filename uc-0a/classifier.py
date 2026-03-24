"""
UC-0A — Complaint Classifier
Implements agents.md role, intent, context, and enforcement rules via skills.md specifications.
"""
import argparse
import csv
import logging
from typing import Dict, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Enforcement rule 1: Valid categories from agents.md
VALID_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Enforcement rule 2: Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category keywords for classification heuristics
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "hole in road", "cavity"],
    "Flooding": ["flood", "water", "waterlogging", "inundation", "overflow"],
    "Streetlight": ["light", "street light", "lamp", "dark", "unlit"],
    "Waste": ["garbage", "trash", "waste", "litter", "rubbish", "dumping"],
    "Noise": ["noise", "sound", "loud", "music", "honking", "construction"],
    "Road Damage": ["road", "pavement", "cracked", "damaged", "broken"],
    "Heritage Damage": ["heritage", "monument", "historical", "temple", "statue", "cultural"],
    "Heat Hazard": ["heat", "temperature", "hot", "heatwave", "scorching"],
    "Drain Blockage": ["drain", "blockage", "clogged", "sewer", "blocked"]
}


def classify_complaint(description: str, complaint_id: Optional[str] = None) -> dict:
    """
    Classify a single complaint description per agents.md enforcement rules.
    
    Args:
        description: Complaint description string
        complaint_id: Optional identifier for tracking
        
    Returns:
        dict with keys: category, priority, reason, flag
    """
    if not description or not isinstance(description, str):
        return {
            "complaint_id": complaint_id or "UNKNOWN",
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Enforcement rule 2: Check for severity keywords to determine Urgent priority
    priority = "Urgent" if any(keyword in description_lower for keyword in SEVERITY_KEYWORDS) else "Standard"
    
    # Attempt to classify into one of the valid categories (Enforcement rule 1)
    category = _classify_category(description_lower, description)
    
    # Enforcement rule 3: Generate reason citing specific complaint language
    reason = _generate_reason(description, category)
    
    # Enforcement rule 4: Set NEEDS_REVIEW flag for ambiguous complaints
    flag = "NEEDS_REVIEW" if category == "Other" and not _is_clearly_ambiguous(description_lower) else ""
    
    return {
        "complaint_id": complaint_id or "",
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description_lower: str, original: str) -> str:
    """
    Classify complaint into one of the valid categories using keyword matching.
    """
    # Score each category based on keyword matches
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in description_lower)
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return "Other"


def _generate_reason(description: str, category: str) -> str:
    """
    Generate a one-sentence reason citing specific words from the description.
    Enforcement rule 3: Must cite specific words directly from complaint description.
    """
    if category == "Other":
        return f"Complaint could not be clearly categorized based on available description."
    
    # Extract key phrases and construct reason
    desc_lower = description.lower()
    words = description.split()
    
    # Try to find a representative excerpt or summary
    if len(words) > 20:
        excerpt = " ".join(words[:30]) + "..."
    else:
        excerpt = description
    
    return f"Complaint about {category.lower()}: {excerpt}"


def _is_clearly_ambiguous(description_lower: str) -> bool:
    """
    Determine if a complaint is genuinely ambiguous (conflicting signals).
    """
    # Count category keyword matches to detect true ambiguity
    matching_categories = [
        cat for cat, keywords in CATEGORY_KEYWORDS.items()
        if any(kw in description_lower for kw in keywords)
    ]
    
    # If 2+ categories match strongly, it's ambiguous
    return len(matching_categories) > 1


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint skill to each row, write output CSV.
    Per skills.md: handles CSV with Description column, produces output with
    category, priority, reason, flag columns. Continues on errors (per error_handling).
    """
    try:
        # Read input CSV
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Validate that description column exists
            if not reader.fieldnames or 'description' not in [f.lower() for f in reader.fieldnames]:
                logger.error(f"Input CSV missing 'description' column. Found: {reader.fieldnames}")
                raise ValueError("Input CSV must contain a 'description' (or 'Description') column")
            
            # Find the actual description column name (case-insensitive)
            desc_column = next(f for f in reader.fieldnames if f.lower() == 'description')
            
            # Collect and classify all rows
            output_rows = []
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                try:
                    description = row.get(desc_column, "").strip()
                    complaint_id = row.get('complaint_id') or row.get('id') or f"ROW_{row_num}"
                    
                    # Apply classify_complaint skill
                    classification = classify_complaint(description, complaint_id)
                    
                    # Preserve original columns and add classification
                    output_row = {**row, **classification}
                    output_rows.append(output_row)
                    
                except Exception as e:
                    # Error handling per skills.md: log error and continue with fallback
                    logger.warning(f"Error processing row {row_num}: {str(e)}")
                    complaint_id = row.get('complaint_id') or row.get('id') or f"ROW_{row_num}"
                    
                    fallback = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Error processing complaint",
                        "flag": "NEEDS_REVIEW"
                    }
                    output_row = {**row, **fallback}
                    output_rows.append(output_row)
        
        # Write output CSV
        if output_rows:
            fieldnames = list(output_rows[0].keys())
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(output_rows)
                logger.info(f"Classified {len(output_rows)} complaints. Results written to {output_path}")
        else:
            logger.warning("No rows to classify")
            
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        raise
    except Exception as e:
        logger.error(f"Batch classification failed: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
