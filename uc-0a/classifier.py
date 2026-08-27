"""
UC-0A — Complaint Classifier
Implementation of complaint classification using RICE framework and enforcement rules.
"""
import argparse
import csv
import sys
import re

# Allowed categories (exact strings only)
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category patterns to match in description (pattern -> category)
CATEGORY_PATTERNS = {
    r'\b(pothole|potholed|potholes|crater|rut)\b': "Pothole",
    r'\b(flood|flooding|flooded|waterlogged|stagnant water|submerged|knee-deep)\b': "Flooding",
    r'\b(streetlight|street light|light out|light|bulb|dark|sparking|electrical)\b': "Streetlight",
    r'\b(waste|garbage|trash|litter|rubbish|bins|dump|dumped|overflowing)\b': "Waste",
    r'\b(noise|music|sound|loud|horn|blaring)\b': "Noise",
    r'\b(road|pavement|footpath|tiles|cracked|sinking|surface|broken|upturned)\b': "Road Damage",
    r'\b(heritage|historic|old city|ancient|monument)\b': "Heritage Damage",
    r'\b(heat|temperature|hot|thermal|burning)\b': "Heat Hazard",
    r'\b(drain|drainage|blocked|blockage)\b': "Drain Blockage",
}

def extract_severity_keywords(description: str) -> list:
    """Extract severity keywords found in description (case-insensitive)."""
    if not description:
        return []
    desc_lower = description.lower()
    found = []
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', desc_lower):
            found.append(keyword)
    return found

def classify_category(description: str) -> tuple:
    """Determine category from description. Returns (category, is_ambiguous)."""
    if not description or not description.strip():
        return ("Other", True)
    
    desc_lower = description.lower()
    matched_categories = []
    
    # Check each pattern against description
    for pattern, category in CATEGORY_PATTERNS.items():
        if re.search(pattern, desc_lower, re.IGNORECASE):
            matched_categories.append(category)
    
    # Remove duplicates and check for ambiguity
    unique_categories = list(set(matched_categories))
    
    if len(unique_categories) == 0:
        return ("Other", True)  # No pattern matched
    elif len(unique_categories) == 1:
        return (unique_categories[0], False)  # Unambiguous
    else:
        # Multiple categories matched - need to disambiguate
        # Prioritize based on description specificity
        if "pothole" in desc_lower and "Pothole" in unique_categories:
            return ("Pothole", False)
        elif "flood" in desc_lower and "Flooding" in unique_categories:
            return ("Flooding", False)
        elif "drain" in desc_lower and "Drain Blockage" in unique_categories:
            return ("Drain Blockage", False)
        else:
            # Genuinely ambiguous - flag for review
            return (unique_categories[0], True)

def generate_reason(description: str, category: str) -> str:
    """Generate a one-sentence reason citing specific words from description."""
    if not description or not description.strip():
        return "No description provided for classification."
    
    # Extract key phrases from description
    words = description.split()
    key_words = []
    for word in words[:15]:  # Look at first 15 words
        if len(word) > 3 and word.lower() not in ['that', 'this', 'area', 'near', 'road', 'ward']:
            key_words.append(word.rstrip('.,'))
    
    # Build reason sentence
    if len(key_words) >= 2:
        first_words = ' '.join(key_words[:2])
        reason = f"Classified as {category} based on complaint mentioning: {first_words}."
    else:
        reason = f"Classified as {category} based on complaint description."
    
    return reason

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforcement rules applied:
    1. Category must be exactly one of allowed values
    2. Priority is Urgent if severity keywords present, otherwise Standard
    3. Reason cites specific words from description
    4. Flag is NEEDS_REVIEW if ambiguous, otherwise empty
    """
    complaint_id = row.get('complaint_id', 'UNKNOWN')
    description = row.get('description', '')
    
    try:
        # Classify category and check for ambiguity
        category, is_ambiguous = classify_category(description)
        
        # Determine priority based on severity keywords
        severity_keywords = extract_severity_keywords(description)
        if severity_keywords:
            priority = "Urgent"
        else:
            priority = "Standard"
        
        # Generate reason
        reason = generate_reason(description, category)
        
        # Set flag for ambiguous cases
        flag = "NEEDS_REVIEW" if is_ambiguous else ""
        
        return {
            'complaint_id': complaint_id,
            'category': category,
            'priority': priority,
            'reason': reason,
            'flag': flag
        }
    except Exception as e:
        # Error handling - return safe defaults
        print(f"ERROR classifying {complaint_id}: {str(e)}", file=sys.stderr)
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': f"Error during classification: {str(e)}",
            'flag': 'NEEDS_REVIEW'
        }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    error_count = 0
    
    try:
        # Read input CSV
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                print(f"ERROR: Input file {input_path} is empty or malformed", file=sys.stderr)
                return
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                try:
                    # Classify this row
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    error_count += 1
                    print(f"ERROR at row {row_num}: {str(e)}", file=sys.stderr)
                    # Add error result
                    complaint_id = row.get('complaint_id', f'ROW_{row_num}')
                    results.append({
                        'complaint_id': complaint_id,
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Row failed to classify',
                        'flag': 'NEEDS_REVIEW'
                    })
        
        # Write output CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        if error_count > 0:
            print(f"Warning: {error_count} rows had errors but were included in output with flag=NEEDS_REVIEW", file=sys.stderr)
    
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
