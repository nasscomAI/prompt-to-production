"""
UC-0A — Complaint Classifier

Implements classify_complaint and batch_classify skills following agents.md integrity rules:
- Taxonomy drift prevention
- Severity blindness prevention (keywords force Urgent)
- Missing justification prevention (citations required)
- Hallucinated categories prevention (exact list only)
- False confidence prevention (ambiguous → NEEDS_REVIEW flag)
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple


# Allowed categories (exact strings only)
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

# Severity keywords that force Urgent priority
SEVERITY_KEYWORDS = {
    'injury', 'child', 'children', 'school', 'hospital', 'ambulance',
    'fire', 'hazard', 'fell', 'collapse', 'collapsed', 'collapsing'
}

# Category keywords for matching
CATEGORY_KEYWORDS = {
    "Pothole": ['pothole', 'pit', 'crater', 'hole in road'],
    "Flooding": ['flood', 'flooded', 'water', 'inundated', 'submerged', 'waterlog'],
    "Streetlight": ['streetlight', 'street light', 'light out', 'lamp', 'lighting', 'bulb'],
    "Waste": ['garbage', 'trash', 'waste', 'litter', 'refuse', 'rubbish', 'dump'],
    "Noise": ['noise', 'sound', 'music', 'loud', 'shouting', 'honking', 'disturb'],
    "Road Damage": ['road damage', 'crack', 'cracked', 'sinking', 'cave', 'surface damage'],
    "Heritage Damage": ['heritage', 'monument', 'historic', 'cultural', 'archaeological'],
    "Heat Hazard": ['heat', 'temperature', 'sun', 'scorch', 'thermal'],
    "Drain Blockage": ['drain', 'blocked', 'blockage', 'clogged', 'sewage', 'gutter'],
}


def extract_keywords(text: str) -> set:
    """Extract lowercase words from text."""
    return set(re.findall(r'\b\w+\b', text.lower()))


def has_severity_keywords(description: str) -> bool:
    """Check if description contains severity keywords (including word variations)."""
    description_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            return True
    return False


def classify_complaint(description: str) -> Dict[str, str]:
    """
    Classify a single complaint description.
    
    Returns:
        Dict with keys: category, priority, reason, flag
    """
    description_lower = description.lower()
    keywords = extract_keywords(description)
    
    # Calculate relevance score for each category
    category_scores = {}
    for category, category_keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in category_keywords if keyword in description_lower)
        if score > 0:
            category_scores[category] = score
    
    # Determine category
    if not category_scores:
        category = "Other"
        reason = f"No clear match to standard categories."
        flag = "NEEDS_REVIEW"
    elif len(category_scores) == 1:
        # Clear single match
        category = list(category_scores.keys())[0]
        flag = ""
        
        # Build reason citing specific words from description
        matched_keywords = [kw for category_kws in [CATEGORY_KEYWORDS[category]] 
                           for kw in category_kws if kw in description_lower]
        if matched_keywords:
            reason = f"Complaint mentions '{matched_keywords[0]}'."
        else:
            reason = f"Complaint matches {category} description."
    else:
        # Multiple potential matches - check for genuine ambiguity
        top_score = max(category_scores.values())
        top_categories = [cat for cat, score in category_scores.items() if score == top_score]
        
        if len(top_categories) > 1:
            # Genuinely ambiguous
            category = top_categories[0]  # Pick first
            flag = "NEEDS_REVIEW"
            reason = f"Complaint could be {' or '.join(top_categories)}."
        else:
            # Clear winner
            category = top_categories[0]
            flag = ""
            matched_keywords = [kw for category_kws in [CATEGORY_KEYWORDS[category]] 
                               for kw in category_kws if kw in description_lower]
            if matched_keywords:
                reason = f"Complaint mentions '{matched_keywords[0]}'."
            else:
                reason = f"Complaint matches {category} description."
    
    # Determine priority
    if has_severity_keywords(description):
        priority = "Urgent"
    else:
        priority = "Standard"
    
    # Validate category is in allowed list
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Enforces:
    - All rows get all four fields (no nulls)
    - Category, priority, reason, flag all present
    - Ambiguous rows flagged NEEDS_REVIEW
    - Exact category strings from allowed list only
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                raise ValueError("Input CSV must have 'description' column")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    complaint_id = row.get('complaint_id', f'ROW_{row_num}')
                    description = row.get('description', '').strip()
                    
                    if not description:
                        results.append({
                            'complaint_id': complaint_id,
                            'description': description,
                            'category': 'Other',
                            'priority': 'Standard',
                            'reason': 'No description provided.',
                            'flag': 'NEEDS_REVIEW'
                        })
                        continue
                    
                    # Classify
                    classification = classify_complaint(description)
                    
                    results.append({
                        'complaint_id': complaint_id,
                        'description': description,
                        'category': classification['category'],
                        'priority': classification['priority'],
                        'reason': classification['reason'],
                        'flag': classification['flag']
                    })
                
                except Exception as e:
                    # Error in row - still output with flags
                    results.append({
                        'complaint_id': row.get('complaint_id', f'ROW_{row_num}'),
                        'description': row.get('description', ''),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Error during classification: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
        
        # Write output CSV
        if not results:
            raise ValueError("No rows processed from input file")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['complaint_id', 'description', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Classified {len(results)} complaints")
        flagged = sum(1 for r in results if r['flag'])
        print(f"Flagged {flagged} for review")
    
    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
