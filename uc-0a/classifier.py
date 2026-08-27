"""
UC-0A — Complaint Classifier
Implements complaint classification with strict RICE rules for consistency.
"""
import argparse
import csv
import re

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = {'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'}

# Category keywords for classification
CATEGORY_KEYWORDS = {
    'Pothole': ['pothole', 'pit', 'hole'],
    'Flooding': ['flood', 'waterlogged', 'water', 'stranded', 'knee-deep'],
    'Streetlight': ['streetlight', 'street light', 'light', 'sparking'],
    'Waste': ['garbage', 'waste', 'trash', 'rubbish', 'dumped', 'animal'],
    'Noise': ['noise', 'music', 'sound', 'loud'],
    'Road Damage': ['road', 'crack', 'surface', 'sinking', 'tiles', 'upturned'],
    'Heritage Damage': ['heritage', 'historic', 'old city'],
    'Drain Blockage': ['drain', 'blocked', 'blockage'],
    'Heat Hazard': ['heat', 'extreme', 'temperature'],
}

def contains_severity_keyword(text: str) -> bool:
    """Check if text contains any severity keywords (case-insensitive)."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SEVERITY_KEYWORDS)

def classify_category(description: str) -> tuple[str, str]:
    """
    Classify complaint into category and return (category, reason).
    Returns tuple of (category, reason_snippet).
    """
    description_lower = description.lower()
    
    # Score each category by keyword matches
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in description_lower)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return 'Other', 'No clear category match.'
    
    # Get top category
    top_category = max(scores, key=scores.get)
    
    # Extract relevant phrase from description for reason
    for keyword in CATEGORY_KEYWORDS[top_category]:
        if keyword in description_lower:
            idx = description_lower.find(keyword)
            start = max(0, idx - 20)
            end = min(len(description), idx + 50)
            reason = description[start:end].strip()
            return top_category, reason
    
    return top_category, description[:50] + "..." if len(description) > 50 else description

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '')
    
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Classify category
    category, reason = classify_category(description)
    
    # Determine priority based on severity keywords
    if contains_severity_keyword(description):
        priority = 'Urgent'
    else:
        priority = 'Standard'
    
    # Determine if needs review (ambiguous cases)
    flag = ''
    # Flag if multiple strong categories or low confidence
    description_lower = description.lower()
    category_count = sum(1 for keywords in CATEGORY_KEYWORDS.values() 
                        for kw in keywords if kw in description_lower)
    if category_count > 3:
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
    Handles errors gracefully and writes all rows even if some fail.
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                print(f"Error: Empty input file {input_path}")
                return
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    if not row.get('complaint_id'):
                        continue
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Log error but continue processing
                    print(f"Warning: Error processing row {row_num}: {e}")
                    results.append({
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Error during classification',
                        'flag': 'NEEDS_REVIEW'
                    })
    
    except Exception as e:
        print(f"Error reading input file {input_path}: {e}")
        return
    
    # Write results
    if not results:
        print(f"Warning: No complaints to classify in {input_path}")
        return
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
