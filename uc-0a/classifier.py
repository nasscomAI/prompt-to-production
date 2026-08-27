"""
UC-0A — Complaint Classifier
Classifies city infrastructure complaints into category, priority, reason, and review flags.
Implemented per agents.md and skills.md enforcement rules.
"""
import argparse
import csv
from typing import Dict, Optional, Tuple, List


# ============================================================================
# KEYWORD MAPPING — Aligned with README and test complaint descriptions
# ============================================================================

KEYWORD_CATEGORIES = {
    "Pothole": ["pothole", "pot hole", "crater", "pavement crack", "asphalt break"],
    "Flooding": ["flood", "waterlogged", "water pool", "standing water", "drain overflow", "inundation"],
    "Streetlight": ["streetlight", "street light", "lamp", "unlit", "dark", "lighting", "bulb"],
    "Waste": ["waste", "garbage", "trash", "litter", "bin", "overflowing", "debris", "dumping"],
    "Noise": ["noise", "sound", "loud", "music", "commotion", "disturbance"],
    "Road Damage": ["road subsidence", "subsidence", "road crack", "surface damage", "pavement damage", "tarmac", "paving", "paved", "asphalt", "bench", "divider", "shelter", "roof", "glass"],
    "Heritage Damage": ["heritage", "historic", "ancient", "step well", "monument", "archaeological"],
    "Heat Hazard": ["heat", "temperature", "melting", "sticking", "burning", "hot", "surface temperature", "°c", "heatwave", "dangerous temperatures", "bubbling"],
    "Drain Blockage": ["drain", "drainage", "blockage", "clogged", "blocked", "sewer"],
}

# Severity keywords that trigger Urgent priority (from agents.md enforcement)
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def keyword_matcher(description: str) -> Tuple[Optional[str], bool, List[str]]:
    """
    Match complaint description text against category and severity keywords.
    
    Returns:
      (category_match, severity_match, matched_words)
      - category_match: str (single matched category) or None (no match or ambiguous)
      - severity_match: bool (True if description contains ANY severity keyword)
      - matched_words: list of specific keywords that matched
    
    Enforces: Case-insensitive matching, no hallucinated sub-categories.
    Priority: Heritage Damage > Heat Hazard > Flooding > single unique category > ambiguous
    """
    if not description or not isinstance(description, str):
        return None, False, []
    
    desc_lower = description.lower()
    matched_categories = []
    matched_words = []
    
    # Check each category's keywords
    for category, keywords in KEYWORD_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in desc_lower:
                matched_categories.append(category)
                matched_words.append(keyword)
                break  # Found this category, move to next
    
    # Determine single category match with priority handling
    category_match = None
    if len(matched_categories) == 1:
        category_match = matched_categories[0]
    elif len(matched_categories) > 1:
        # Multiple matches — use priority: Heritage > Heat Hazard > Flooding > ambiguous
        if "Heritage Damage" in matched_categories:
            category_match = "Heritage Damage"
        elif "Heat Hazard" in matched_categories:
            category_match = "Heat Hazard"
        elif "Flooding" in matched_categories:
            category_match = "Flooding"
        else:
            # Ambiguous — signal for review
            category_match = None
    
    # Check for severity keywords
    severity_match = any(sev.lower() in desc_lower for sev in SEVERITY_KEYWORDS)
    
    return category_match, severity_match, matched_words


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Input: dict with keys: complaint_id, description, location, days_open (or any subset)
    Output: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces: No crash on malformed input, all required fields present, category exact match,
    priority logic per severity keywords, reason cites specific description text, ambiguities flagged.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip() if row.get("description") else ""
    days_open = row.get("days_open", 0)
    
    # Convert days_open to int (error handling per skills.md)
    try:
        days_open = int(days_open) if days_open else 0
    except (ValueError, TypeError):
        days_open = 0
    
    # Handle missing or malformed description (enforcement: do not crash, flag for review)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty.",
            "flag": "NEEDS_REVIEW",
        }
    
    # Keyword matching (skill: keyword_matcher)
    category_match, severity_match, matched_words = keyword_matcher(description)
    
    # Determine category (enforcement: EXACTLY one of allowed values)
    if category_match:
        category = category_match
        # Reason must cite specific words from description (enforcement rule)
        cited_words = ", ".join(matched_words[:2]) if matched_words else "complaint description"
        reason = f"Description mentions: {cited_words}."
        flag = ""
    else:
        # Ambiguous or no match (enforcement: output Other, flag NEEDS_REVIEW)
        category = "Other"
        reason = "Complaint description does not match known infrastructure categories."
        flag = "NEEDS_REVIEW"
    
    # Determine priority (enforcement: Urgent if severity keywords present)
    if severity_match:
        priority = "Urgent"
    elif days_open > 60:
        priority = "Low"
    else:
        priority = "Standard"
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    
    Input CSV columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    Output CSV columns: complaint_id, category, priority, reason, flag
    
    Enforces: Flag nulls, not crash on bad rows, produce output even if some rows fail (per skills.md).
    """
    try:
        rows_classified = 0
        
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV is empty or has no headers.")
            
            writer = csv.DictWriter(
                outfile,
                fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
            )
            writer.writeheader()
            
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    writer.writerow(classified)
                    rows_classified += 1
                except Exception as e:
                    # Catch any row-level exceptions, flag and continue (enforcement: do not crash)
                    complaint_id = row.get("complaint_id", "UNKNOWN")
                    writer.writerow({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing error: {str(e)[:50]}",
                        "flag": "NEEDS_REVIEW",
                    })
                    rows_classified += 1
        
        print(f"Classified {rows_classified} complaints. Results written to {output_path}")
    
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        raise
    except Exception as e:
        print(f"Error during classification: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
