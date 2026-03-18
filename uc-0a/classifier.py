"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'}

# Valid categories
VALID_CATEGORIES = {
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
}

# Category detection patterns
CATEGORY_PATTERNS = {
    'Pothole': r'\b(pothole|pot hole|crater|pit|hole|tyre damage)\b',
    'Flooding': r'\b(flood|water|wet|knee-deep|submerged|waterlog|inundated)\b',
    'Streetlight': r'\b(streetlight|street light|light|lamp|illumination|dark|sparking|electrical)\b',
    'Waste': r'\b(waste|garbage|bin|trash|dump|dumped|litter|debris|animal|smell)\b',
    'Noise': r'\b(noise|music|sound|loud|loudly|past midnight)\b',
    'Road Damage': r'\b(road|surface|cracked|sinking|damage|crack|pothole|pit)\b',
    'Heritage Damage': r'\b(heritage|heritage street|old|historic|ancient)\b',
    'Heat Hazard': r'\b(heat|temperature|hot|thermal)\b',
    'Drain Blockage': r'\b(drain|blocked|blockage|clogged)\b',
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implements RICE enforcement rules:
    - Exact category names from allowed list
    - Urgent priority for severity keywords
    - Reason cites specific words from description
    - Flag set for ambiguous classifications
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').lower()
    
    category = 'Other'
    flag = ''
    reason = 'No description provided.'
    
    if description:
        # Count category matches
        matches = {}
        for cat, pattern in CATEGORY_PATTERNS.items():
            if re.search(pattern, description, re.IGNORECASE):
                matches[cat] = len(re.findall(pattern, description, re.IGNORECASE))
        
        if matches:
            # Sort by most matches, pick top category
            sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
            category = sorted_matches[0][0]
            
            # Flag if genuinely ambiguous (multiple strong candidates)
            if len(sorted_matches) > 1 and sorted_matches[0][1] == sorted_matches[1][1]:
                flag = 'NEEDS_REVIEW'
            
            # Extract reason: find key phrase from description
            for pattern_text in CATEGORY_PATTERNS[category].split('|'):
                pattern_text = pattern_text.replace(r'\b', '').replace('(', '').replace(')', '')
                if pattern_text.strip() in description:
                    keywords = [w for w in description.split() if pattern_text.strip() in w]
                    if keywords:
                        reason = f"Complaint mentions {pattern_text.strip()}."
                        break
        else:
            reason = "No clear category indicators found."
    
    # Check priority: Urgent if severity keywords present
    priority = 'Standard'
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', description, re.IGNORECASE):
            priority = 'Urgent'
            break
    
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
    
    Handles errors gracefully:
    - Skips rows with missing complaint_id
    - Continues on bad rows
    - Always produces output
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
