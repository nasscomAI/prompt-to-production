"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
Core failure modes prevented: Taxonomy drift · Severity blindness · Missing justification · 
Hallucinated sub-categories · False confidence on ambiguity
"""
import argparse
import csv
import sys
import re

# PREVENT TAXONOMY DRIFT: Exact category strings only
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# PREVENT SEVERITY BLINDNESS: Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implements RICE enforcement rules from agents.md:
    - PREVENT TAXONOMY DRIFT: Uses exact category strings only
    - PREVENT SEVERITY BLINDNESS: Case-insensitive severity keyword matching
    - PREVENT MISSING JUSTIFICATION: Always includes reason citing specific words
    - PREVENT HALLUCINATED SUB-CATEGORIES: No variations, one exact category per row
    - PREVENT FALSE CONFIDENCE ON AMBIGUITY: Flags ambiguous cases as NEEDS_REVIEW
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').strip()
    
    # Handle missing/empty description
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'No description provided',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Normalize description for keyword matching
    description_lower = description.lower()
    
    # PREVENT SEVERITY BLINDNESS: Check for severity keywords (case-insensitive)
    has_severity_keyword = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)
    
    # Classify category based on keywords in description
    category = 'Other'
    reason = ''
    flag = ''
    
    # Pattern matching for category classification
    if re.search(r'\b(pothole|pot hole|road crater|hole in road)\b', description_lower):
        category = 'Pothole'
        reason = f"Description mentions pothole/road damage: '{description[:50]}...'"
    elif re.search(r'\b(flood|flooding|flooded|floods|water logging|water logged|inundated|submerg)\b', description_lower):
        category = 'Flooding'
        reason = f"Description mentions flooding/water logging: '{description[:50]}...'"
    elif re.search(r'\b(street ?lights?|lamp post|street lamp|light(s)? (not working|out)|lamp out)\b', description_lower):
        category = 'Streetlight'
        reason = f"Description mentions streetlight issues: '{description[:50]}...'"
    elif re.search(r'\b(waste|garbage|trash|litter|dump|refuse|rubbish)\b', description_lower):
        category = 'Waste'
        reason = f"Description mentions waste/garbage: '{description[:50]}...'"
    elif re.search(r'\b(noise|loud|sound|decibel|music|speaker)\b', description_lower):
        category = 'Noise'
        reason = f"Description mentions noise issues: '{description[:50]}...'"
    elif re.search(r'\b(road damage|road crack|road break|road surface|pavement damage|asphalt|footpath.*broken|tiles.*broken)\b', description_lower):
        category = 'Road Damage'
        reason = f"Description mentions road damage: '{description[:50]}...'"
    elif re.search(r'\b(heritage|historic|monument|ancient|cultural site|protected)\b', description_lower):
        category = 'Heritage Damage'
        reason = f"Description mentions heritage/historic site: '{description[:50]}...'"
    elif re.search(r'\b(heat|hot|temperature|heat wave|swelter|sun)\b', description_lower):
        category = 'Heat Hazard'
        reason = f"Description mentions heat hazard: '{description[:50]}...'"
    elif re.search(r'\b(drain|drainage|sewer|clog|block|gutter|manhole)\b', description_lower):
        category = 'Drain Blockage'
        reason = f"Description mentions drain/drainage blockage: '{description[:50]}...'"
    else:
        # PREVENT FALSE CONFIDENCE ON AMBIGUITY
        category = 'Other'
        reason = f"Cannot determine specific category from description: '{description[:50]}...'"
        flag = 'NEEDS_REVIEW'
    
    # PREVENT MISSING JUSTIFICATION: Ensure reason cites specific words
    if not reason:
        reason = f"Classified based on description: '{description[:50]}...'"
    
    # Determine priority
    if has_severity_keyword:
        priority = 'Urgent'
        # Add severity keyword to reason
        matched_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
        reason += f" Contains severity keywords: {', '.join(matched_keywords)}."
    elif category in ['Pothole', 'Flooding', 'Road Damage', 'Drain Blockage', 'Streetlight']:
        priority = 'Standard'
    else:
        priority = 'Low'
    
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
    
    Handles malformed rows gracefully, produces output even if some rows fail.
    Ensures consistent category naming to prevent taxonomy drift.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Validate input columns
            if not all(col in reader.fieldnames for col in ['complaint_id', 'description']):
                print(f"Error: Input CSV must contain 'complaint_id' and 'description' columns", file=sys.stderr)
                sys.exit(1)
            
            results = []
            row_number = 0
            
            for row in reader:
                row_number += 1
                try:
                    # Classify the complaint
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Handle classification errors gracefully
                    print(f"Warning: Error classifying row {row_number}: {e}", file=sys.stderr)
                    results.append({
                        'complaint_id': row.get('complaint_id', f'row_{row_number}'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f'Classification error: {str(e)[:50]}',
                        'flag': 'NEEDS_REVIEW'
                    })
            
            # Write output CSV
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
                
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Cannot write to output file '{output_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
