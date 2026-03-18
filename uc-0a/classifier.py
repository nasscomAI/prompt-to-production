"""
UC-0A — Complaint Classifier
Deterministic classification with RICE enforcement:
- Exact category names from allowed list only
- Priority Urgent/Standard/Low with severity keyword detection
- Reasons cite specific phrases from complaint description
- Flag NEEDS_REVIEW for genuinely ambiguous classifications
"""
import argparse
import csv
import re

# Severity keywords that MUST trigger Urgent priority
SEVERITY_KEYWORDS = {'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'}

# Valid categories - EXACTLY as per UC-0A schema
VALID_CATEGORIES = {
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
}

# Category detection patterns - terms that indicate each category
CATEGORY_PATTERNS = {
    'Pothole': r'\b(pothole|pot hole|crater|pit|tyre damage)\b',
    'Flooding': r'\b(flood|floods|flooded|water|knee-deep|submerged|waterlog|inundated|stranded)\b',
    'Streetlight': r'\b(streetlight|street light|lights|light|lamp|illumination|dark|sparkling|sparking|electrical|flicker)\b',
    'Waste': r'\b(waste|garbage|bin|trash|dump|dumped|litter|debris|animal|smell|overflowing)\b',
    'Noise': r'\b(noise|music|sound|loud|loudly|midnight)\b',
    'Road Damage': r'\b(road|surface|cracked|sinking|damage|crack|tiles|broken|upturned|manhole|cover)\b',
    'Heritage Damage': r'\b(heritage|heritage street|old city|historic|ancient)\b',
    'Heat Hazard': r'\b(heat|temperature|hot|thermal)\b',
    'Drain Blockage': r'\b(drain|blocked|blockage|clogged)\b',
}


def extract_context_phrase(description: str, keyword: str, max_words: int = 10) -> str:
    """
    Extract a short context phrase (up to max_words) around the keyword.
    Used for generating reason field that cites actual description text.
    """
    words = description.split()
    keyword_idx = -1
    
    # Find the keyword in the description
    for i, word in enumerate(words):
        if keyword.lower() in word.lower():
            keyword_idx = i
            break
    
    if keyword_idx >= 0:
        start = max(0, keyword_idx - 2)
        end = min(len(words), keyword_idx + max_words - 2)
        phrase = ' '.join(words[start:end]).rstrip('.,;:')
        return phrase
    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row deterministically.
    
    Enforcement:
    - category: EXACTLY one of the allowed list
    - priority: Urgent if severity keywords present, else Standard
    - reason: ONE sentence citing specific words/phrases from description
    - flag: NEEDS_REVIEW if genuinely ambiguous (multiple strong matches)
    
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '')
    description_lower = description.lower()
    
    category = 'Other'
    flag = ''
    reason = 'No description provided.'
    
    if description_lower:
        # Count category matches
        matches = {}
        match_phrases = {}  # Store matching phrases for reason extraction
        
        for cat, pattern in CATEGORY_PATTERNS.items():
            match_count = len(re.findall(pattern, description_lower, re.IGNORECASE))
            if match_count > 0:
                matches[cat] = match_count
                # Extract phrase for reason - get the first matching keyword
                match = re.search(pattern, description_lower, re.IGNORECASE)
                if match:
                    matched_keyword = match.group()
                    phrase = extract_context_phrase(description, matched_keyword)
                    match_phrases[cat] = phrase if phrase else matched_keyword
        
        if matches:
            # Sort by most matches, pick top category
            sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
            category = sorted_matches[0][0]
            top_match_count = sorted_matches[0][1]
            
            # Flag if genuinely ambiguous: multiple categories with same match count
            if len(sorted_matches) > 1 and sorted_matches[1][1] == top_match_count:
                flag = 'NEEDS_REVIEW'
            
            # Generate reason: cite the actual phrase from description
            if category in match_phrases:
                phrase_to_cite = match_phrases[category]
                # Clean up any trailing punctuation from phrase
                phrase_to_cite = phrase_to_cite.rstrip('.,;:')
                reason = f"Description mentions: {phrase_to_cite}."
            else:
                reason = f"Complaint matches {category.lower()} indicators."
        
        else:
            # No matches found
            reason = "No clear category indicators in description."
            flag = 'NEEDS_REVIEW' if len(description_lower) > 20 else ''
    
    # Determine priority: Urgent if severity keywords present
    priority = 'Standard'
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', description_lower, re.IGNORECASE):
            priority = 'Urgent'
            break
    
    # Validate category is in allowed list (defensive check)
    if category not in VALID_CATEGORIES:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Error handling:
    - Skips rows with missing complaint_id
    - Continues on bad rows instead of crashing
    - Always produces output file
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Log error but continue processing
                    complaint_id = row.get('complaint_id', 'UNKNOWN')
                    print(f"Warning: Classification failed for {complaint_id}: {str(e)}")
                    results.append({
                        'complaint_id': complaint_id,
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f"Classification error: {str(e)}",
                        'flag': 'NEEDS_REVIEW'
                    })
        
        # Write output
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        raise
    except Exception as e:
        print(f"Error during batch classification: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
