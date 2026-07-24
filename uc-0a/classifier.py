"""
UC-0A — Complaint Classifier
Implements citizen complaint classification following RICE enforcement rules.

Classification Schema:
- Categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, 
              Heritage Damage, Heat Hazard, Drain Blockage, Other
- Priority: Urgent (severity keywords), Standard (infrastructure), Low (minor)
- Severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
"""
import argparse
import csv
import re
from typing import Optional


# === CLASSIFICATION SCHEMA (from agents.md enforcement rules) ===

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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Category detection patterns - order matters (more specific first)
CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpothole\b", r"\bpot\s*hole\b"
    ],
    "Flooding": [
        r"\bflood(?:ed|ing|s)?\b", r"\bwaterlog(?:ged|ging)?\b", 
        r"\bstrand(?:ed)?\b.*(?:water|rain)", r"\bknee[- ]?deep\b",
        r"\bsubmerg(?:ed|ing)?\b", r"\bwater\s*level\b"
    ],
    "Streetlight": [
        r"\bstreetlight\b", r"\bstreet\s*light\b", r"\blights?\s*out\b",
        r"\blight(?:s)?\s*(?:not working|flickering|sparking|broken)\b",
        r"\bdark\s*(?:at night|area)\b", r"\bno\s*light(?:ing)?\b"
    ],
    "Waste": [
        r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\blitter\b",
        r"\boverflowing\s*(?:bins?|garbage)\b", r"\bdead\s*animal\b",
        r"\bdump(?:ed|ing)?\b", r"\brefuse\b", r"\bsmell\b", r"\bstench\b"
    ],
    "Noise": [
        r"\bnoise\b", r"\bloud\b", r"\bmusic\b.*(?:past|after)\s*midnight",
        r"\bdisturbance\b", r"\bmidnight\b.*(?:music|noise|loud)"
    ],
    "Road Damage": [
        r"\broad\s*(?:surface|damage)\b", r"\bcrack(?:ed|s|ing)?\b.*(?:road|surface)\b",
        r"\bsinking\b", r"\bbroken\s*(?:tiles?|footpath|pavement)\b",
        r"\bfootpath\s*(?:tiles?|broken|damaged)\b", r"\bupturned\b",
        r"\bmanhole\s*(?:cover)?\s*missing\b", r"\bpavement\s*damage\b"
    ],
    "Heritage Damage": [
        r"\bheritage\b", r"\bhistoric(?:al)?\b.*(?:damage|risk)\b",
        r"\bmonument\b", r"\bold\s*city\b.*(?:damage|risk|safety)\b"
    ],
    "Heat Hazard": [
        r"\bheat\s*(?:hazard|wave|stroke)\b", r"\bextreme\s*heat\b",
        r"\bsunstroke\b", r"\bhot\s*pavement\b"
    ],
    "Drain Blockage": [
        r"\bdrain\s*(?:block(?:ed|age)?|clogg?ed)\b", r"\bblock(?:ed|age)\b.*drain\b",
        r"\bclogg?ed\s*drain\b", r"\bsewer\s*block\b"
    ]
}


def _check_severity_keywords(text: str) -> tuple[bool, Optional[str]]:
    """
    Check if text contains any severity keywords that trigger Urgent priority.
    Returns: (is_urgent, matched_keyword)
    """
    text_lower = text.lower()
    for keyword in SEVERITY_KEYWORDS:
        if re.search(rf"\b{keyword}\b", text_lower):
            return True, keyword
    return False, None


def _detect_category(description: str) -> tuple[str, float, list[str]]:
    """
    Detect the most likely category from description.
    Returns: (category, confidence, matched_terms)
    
    Confidence: 1.0 = clear match, 0.5 = ambiguous/multiple matches, 0.0 = no match
    """
    description_lower = description.lower()
    matches = {}
    
    for category, patterns in CATEGORY_PATTERNS.items():
        matched_terms = []
        for pattern in patterns:
            found = re.findall(pattern, description_lower, re.IGNORECASE)
            if found:
                matched_terms.extend(found)
        if matched_terms:
            matches[category] = matched_terms
    
    if not matches:
        return "Other", 0.0, []
    
    if len(matches) == 1:
        category = list(matches.keys())[0]
        return category, 1.0, matches[category]
    
    # Multiple matches - determine dominant category by match count
    sorted_matches = sorted(matches.items(), key=lambda x: len(x[1]), reverse=True)
    top_category, top_terms = sorted_matches[0]
    second_category, second_terms = sorted_matches[1]
    
    # If top category has significantly more matches, use it
    if len(top_terms) > len(second_terms):
        return top_category, 0.8, top_terms
    
    # Truly ambiguous - equal matches
    return top_category, 0.5, top_terms


def _determine_priority(description: str, category: str) -> tuple[str, Optional[str]]:
    """
    Determine priority based on severity keywords and category.
    Returns: (priority, severity_keyword_if_any)
    """
    is_urgent, keyword = _check_severity_keywords(description)
    
    if is_urgent:
        return "Urgent", keyword
    
    # Standard priority for infrastructure issues
    infrastructure_categories = [
        "Pothole", "Flooding", "Streetlight", "Road Damage", 
        "Drain Blockage", "Heritage Damage", "Heat Hazard"
    ]
    
    if category in infrastructure_categories:
        return "Standard", None
    
    # Low priority for nuisances (Noise, minor Waste, Other)
    if category in ["Noise", "Other"]:
        return "Low", None
    
    # Waste is Standard by default (health concern)
    if category == "Waste":
        return "Standard", None
    
    return "Standard", None


def _generate_reason(description: str, category: str, priority: str, 
                     matched_terms: list[str], severity_keyword: Optional[str]) -> str:
    """
    Generate a reason citing specific words from the description.
    """
    # Get a representative term from matched terms
    cited_term = matched_terms[0] if matched_terms else "general concern"
    
    if severity_keyword:
        return f"Classified as {category} due to '{cited_term}'; marked Urgent due to '{severity_keyword}' indicating safety risk."
    
    if category == "Other":
        return f"Could not match to specific category; description mentions '{cited_term if matched_terms else 'unrecognized issue'}'."
    
    return f"Classified as {category} based on description mentioning '{cited_term}'."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Args:
        row: Dictionary with complaint data. Required key: 'description'.
             Optional: complaint_id, date_raised, city, ward, location, reported_by, days_open
    
    Returns:
        Dictionary with keys: complaint_id, category, priority, reason, flag
    
    Enforcement rules from agents.md:
    - Category must be exactly one of 10 allowed values
    - Priority is Urgent if severity keywords present
    - Reason must cite specific words from description
    - Flag is NEEDS_REVIEW for ambiguous cases
    """
    # Extract complaint_id, default to UNKNOWN
    complaint_id = row.get("complaint_id", "UNKNOWN")
    if not complaint_id or str(complaint_id).strip() == "":
        complaint_id = "UNKNOWN"
    
    # Get description
    description = row.get("description", "")
    
    # Handle empty/null description
    if not description or str(description).strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    description = str(description).strip()
    
    # Detect category
    category, confidence, matched_terms = _detect_category(description)
    
    # Determine priority
    priority, severity_keyword = _determine_priority(description, category)
    
    # Generate reason citing specific words
    reason = _generate_reason(description, category, priority, matched_terms, severity_keyword)
    
    # Set flag for ambiguous cases
    flag = ""
    if confidence < 0.6:  # Low confidence or no match
        flag = "NEEDS_REVIEW"
    
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
    
    Args:
        input_path: Path to input CSV file with complaint data
        output_path: Path to write results CSV
    
    Robustness (from skills.md):
    - Handles missing files with clear error
    - Handles empty files (writes headers only)
    - Never crashes on bad rows - marks them for review
    - Generates complaint_id if missing
    """
    # Read input CSV
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")
    
    # Process each row
    results = []
    for i, row in enumerate(rows, start=1):
        try:
            # Ensure complaint_id exists
            if "complaint_id" not in row or not row["complaint_id"]:
                row["complaint_id"] = f"ROW_{i}"
            
            result = classify_complaint(row)
            results.append(result)
            
        except Exception as e:
            # Don't crash on bad rows - mark for review
            results.append({
                "complaint_id": row.get("complaint_id", f"ROW_{i}"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
    
    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
