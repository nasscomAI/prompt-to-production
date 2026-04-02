"""
UC-0A — Complaint Classifier
Built using agents.md and skills.md specifications.
"""
import argparse
import csv
import re

# Classification schema from README.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

# Keyword mappings for categories (simple rule-based classification)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "crater", "dip"],
    "Flooding": ["flood", "water", "inundated", "rain", "overflow"],
    "Streetlight": ["streetlight", "light", "bulb", "dark", "street lamp"],
    "Waste": ["waste", "garbage", "trash", "litter", "dump"],
    "Noise": ["noise", "loud", "sound", "music", "party"],
    "Road Damage": ["road", "damage", "crack", "broken", "pavement"],
    "Heritage Damage": ["heritage", "monument", "historical", "damage", "statue"],
    "Heat Hazard": ["heat", "hot", "temperature", "sun", "scorching"],
    "Drain Blockage": ["drain", "blocked", "sewage", "clog", "pipe"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Follows enforcement rules from agents.md:
    - Category: exact strings from allowed values
    - Priority: Urgent if severity keywords present
    - Reason: one sentence citing specific words
    - Flag: NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').lower()
    
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Invalid input: missing description',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Determine category
    category = 'Other'
    matched_categories = []
    cited_words = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    cited_words.append(keyword)
                break
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # Ambiguous - multiple matches
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        reason = f"Ambiguous complaint matching multiple categories: {', '.join(matched_categories)}. Cited words: {', '.join(cited_words)}."
    else:
        # No matches - Other
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        reason = f"No clear category match. Description contains: {description[:50]}..."
    
    # Determine priority
    priority = 'Standard'
    urgent_cited = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = 'Urgent'
            urgent_cited.append(keyword)
    
    # Build reason if not already set
    if 'reason' not in locals():
        if category != 'Other':
            reason = f"Complaint classified as {category} due to presence of '{', '.join(cited_words)}' in description."
        if priority == 'Urgent':
            reason += f" Marked as Urgent due to '{', '.join(urgent_cited)}'."
        reason = reason.strip()
    
    flag = 'NEEDS_REVIEW' if category == 'Other' and len(matched_categories) != 1 else ''
    
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
    
    Error handling: Skip invalid rows, continue processing, log errors.
    """
    results = []
    error_count = 0
    
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, start=2):  # start=2 because header is 1
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row_num}: {e}")
                    error_count += 1
                    # Add error row
                    results.append({
                        'complaint_id': row.get('complaint_id', f'row_{row_num}'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f'Processing error: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Write output CSV
    if results:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing output file: {e}")
            return
    
    print(f"Processed {len(results)} rows, {error_count} errors. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
