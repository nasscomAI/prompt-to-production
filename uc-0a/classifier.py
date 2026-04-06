"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'}

# Valid categories from taxonomy
VALID_CATEGORIES = {
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
}

# Category triggers — keywords that suggest each category
CATEGORY_TRIGGERS = {
    'Pothole': {'pothole', 'crater', 'divot', 'wheel'},
    'Flooding': {'flood', 'flooded', 'submerged', 'waterlog', 'inundated', 'overflow'},
    'Streetlight': {'light', 'lamp', 'dark', 'illumination', 'streetlight'},
    'Waste': {'waste', 'garbage', 'litter', 'trash', 'debris'},
    'Noise': {'noise', 'drilling', 'idling', 'sound', 'vibration'},
    'Road Damage': {'collapsed', 'crater', 'cracked', 'damaged', 'subsidence'},
    'Heritage Damage': {'heritage', 'historic', 'monument', 'tourist', 'cultural'},
    'Heat Hazard': {'heat', 'temperature', 'exposed'},
    'Drain Blockage': {'drain', 'blockage', 'clogged', 'blocked'},
}

def extract_severity_keywords(description: str) -> list:
    """Extract severity keywords found in description (case-insensitive)."""
    if not description:
        return []
    text = description.lower()
    found = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            found.append(keyword)
    return found

def map_category(description: str) -> tuple:
    """
    Map description to category. Returns (category, matched_triggers, ambiguity_flag).
    Ambiguity flag is True if multiple categories match equally.
    """
    if not description:
        return 'Other', [], True
    
    text = description.lower()
    matches = {}  # category -> list of matched triggers
    
    for category, triggers in CATEGORY_TRIGGERS.items():
        matched = [t for t in triggers if t in text]
        if matched:
            matches[category] = matched
    
    # If no matches, return Other with ambiguity flag
    if not matches:
        return 'Other', [], False
    
    # If single category matches, return it
    if len(matches) == 1:
        category = list(matches.keys())[0]
        triggers = matches[category]
        # Check for potential ambiguity (e.g., both Flooding and Drain Blockage)
        if category == 'Flooding' and 'drain' in text and 'blockage' in text:
            return category, triggers, True
        return category, triggers, False
    
    # Multiple categories match — needs review
    # Prefer most specific (longest match list) or first match
    best_category = max(matches.keys(), key=lambda c: len(matches[c]))
    return best_category, matches[best_category], True

def generate_reason(category: str, description: str, triggers: list) -> str:
    """Generate a reason sentence that cites specific words from description."""
    if not description:
        return "No description provided."
    
    # Extract a snippet that contains at least one trigger
    text = description.lower()
    sentences = [s.strip() for s in description.split('.') if s.strip()]
    
    # Find sentence containing a trigger
    for sentence in sentences:
        if any(trigger in sentence.lower() for trigger in triggers):
            return sentence[:100].rstrip() + "."  # Limit to ~100 chars
    
    # Fallback: use first sentence
    if sentences:
        return sentences[0][:100].rstrip() + "."
    
    return description[:100].rstrip() + "."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    RICE enforcement:
    - Category must be from valid taxonomy
    - Priority is Urgent if severity keywords present, else Standard
    - Reason must cite description
    - Flag NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '')
    
    # Extract severity keywords
    severity_found = extract_severity_keywords(description)
    priority = 'Urgent' if severity_found else 'Standard'
    
    # Map to category
    category, triggers, ambiguous = map_category(description)
    
    # Generate reason citing the description
    reason = generate_reason(category, description, triggers)
    
    # Set flag
    flag = 'NEEDS_REVIEW' if ambiguous else ''
    
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
    
    Handles errors gracefully: logs failures and outputs default classification.
    Produces output even if some rows fail.
    """
    results = []
    urgent_count = 0
    standard_count = 0
    needs_review_count = 0
    rows_processed = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                    rows_processed += 1
                    
                    # Update counts
                    if classification['priority'] == 'Urgent':
                        urgent_count += 1
                    else:
                        standard_count += 1
                    
                    if classification['flag'] == 'NEEDS_REVIEW':
                        needs_review_count += 1
                
                except Exception as e:
                    # Default classification on error
                    classification = {
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Classification error: {str(e)[:50]}',
                        'flag': 'NEEDS_REVIEW'
                    }
                    results.append(classification)
                    rows_processed += 1
                    standard_count += 1
                    needs_review_count += 1
    
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"ERROR reading input file: {e}")
        return
    
    # Write results CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR writing output file: {e}")
        return
    
    # Print summary
    print(f"Classification complete.")
    print(f"Rows processed: {rows_processed}")
    print(f"  - Urgent: {urgent_count}")
    print(f"  - Standard: {standard_count}")
    print(f"  - NEEDS_REVIEW flags: {needs_review_count}")
    print(f"Results written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

