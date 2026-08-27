"""
UC-0A — Complaint Classifier
RICE → agents.md → skills.md → CRAFT implementation.

Enforces:
1. Category: exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
2. Priority: Urgent if severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) present; else Standard
3. Reason: one sentence citing specific words from description
4. Flag: NEEDS_REVIEW if category is ambiguous; blank otherwise
"""
import argparse
import csv
import sys
import re
from typing import Dict, Optional

# Allowed categories (from README)
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

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category patterns for matching descriptions
CATEGORY_PATTERNS = {
    "Pothole": r"\b(pothole|pit|crater|hole|broken.*road|road.*broken|asphalt.*damage)\b",
    "Flooding": r"\b(flood|water.*clogged|water.*overflow|waterlog|inundated|submerge|drowned)\b",
    "Streetlight": r"\b(light|lamp|bulb|dark|streetlight|street.*light|not.*light|light.*off)\b",
    "Waste": r"\b(waste|garbage|trash|litter|dump|dumping|rubble|debris|junk)\b",
    "Noise": r"\b(noise|sound|loud|disturb|horn|music|voice)\b",
    "Road Damage": r"\b(road.*damage|damage.*road|cracked|crack|broken|damage.*surface|surface.*damage)\b",
    "Heritage Damage": r"\b(heritage|historical|monument|ancient|cultural|historic.*site|protect.*site)\b",
    "Heat Hazard": r"\b(heat|hot|temperature|extreme.*heat|heatwave|scorch)\b",
    "Drain Blockage": r"\b(drain.*block|block.*drain|clogged|blockage|drainage|sewer|sewage)\b"
}


def classify_complaint(description: str) -> Dict[str, str]:
    """
    Classify a single complaint based on description.
    
    Args:
        description: Complaint description text
        
    Returns:
        Dict with keys: category, priority, reason, flag
        
    Enforces agents.md rules:
    - Category from ALLOWED_CATEGORIES only
    - Priority Urgent if severity keywords present
    - Reason cites specific words from description
    - Flag=NEEDS_REVIEW if ambiguous, else blank
    """
    
    # Handle empty/null descriptions
    if not description or not isinstance(description, str) or not description.strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Detect severity keywords
    severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
    priority = "Urgent" if severity_found else "Standard"
    
    # Match category using patterns
    matched_categories = []
    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, description_lower, re.IGNORECASE):
            matched_categories.append(category)
    
    # Determine category and flag
    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        # Extract first few words as reason
        words = description.split()[:5]
        reason = f"Could not match to known categories. Description: {' '.join(words)}..."
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        # Extract evidence words
        evidence_words = []
        for word in description_lower.split():
            word_clean = re.sub(r'[^\w]', '', word)
            if word_clean and len(word_clean) > 3:
                evidence_words.append(word_clean)
        evidence = " ".join(evidence_words[:3]) if evidence_words else "issue"
        reason = f"{category}: description mentions {evidence}."
    else:
        # Multiple matches = ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous: could match {', '.join(matched_categories)}."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Enforces skills.md error handling:
    - Flags null descriptions
    - Logs malformed rows to stderr
    - Continues processing on errors
    - Preserves row order
    """
    rows_processed = 0
    rows_failed = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Validate expected columns
            if not reader.fieldnames:
                print("ERROR: Input CSV is empty", file=sys.stderr)
                return
            
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=['id', 'category', 'priority', 'reason', 'flag'])
                writer.writeheader()
                
                for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header
                    try:
                        # Extract description
                        description = row.get('description', '').strip()
                        complaint_id = row.get('id', f"row_{row_num}")
                        
                        # Classify
                        result = classify_complaint(description)
                        
                        # Write output row
                        writer.writerow({
                            'id': complaint_id,
                            'category': result['category'],
                            'priority': result['priority'],
                            'reason': result['reason'],
                            'flag': result['flag']
                        })
                        rows_processed += 1
                        
                    except Exception as e:
                        print(f"ERROR at row {row_num}: {str(e)}", file=sys.stderr)
                        rows_failed += 1
                        continue
        
        print(f"Processed {rows_processed} rows successfully. Failed: {rows_failed}.", file=sys.stderr)
        
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR reading input file: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
