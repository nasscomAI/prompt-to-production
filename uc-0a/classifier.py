"""
UC-0A — Complaint Classifier
Implements complaint classification with strict taxonomy enforcement, severity keyword matching,
and ambiguity flagging per agents.md and skills.md specifications.
"""
import argparse
import csv
import re

# ============================================================================
# CONSTANTS
# ============================================================================

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that MUST trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

VALID_PRIORITIES = ["Urgent", "Standard", "Low"]

# Category keyword patterns (for matching)
CATEGORY_PATTERNS = {
    "Pothole": [r"pothole", r"crater", r"pavement", r"tyre damage"],
    "Flooding": [r"flood", r"waterlogged", r"inundated", r"submerged", r"water", r"stranded", r"knee-deep"],
    "Streetlight": [r"streetlight", r"lamppost", r"light", r"dark", r"illumination", r"sparking", r"flickering"],
    "Waste": [r"garbage", r"waste", r"trash", r"rubbish", r"dumped", r"litter", r"bins", r"animal"],
    "Noise": [r"music", r"noise", r"sound", r"horn", r"loud", r"midnight"],
    "Road Damage": [r"road.*cracked", r"road.*sinking", r"surface.*cracked", r"cracked.*road"],
    "Heritage Damage": [r"heritage", r"historic", r"old city", r"historic street"],
    "Heat Hazard": [r"heat", r"hot", r"temperature", r"thermal"],
    "Drain Blockage": [r"drain.*block", r"clogged.*drain", r"blocked.*drain", r"blockage"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_citation(description: str, category: str, max_length: int = 60) -> str:
    """Extract a short phrase from description relevant to category for citation."""
    desc_lower = description.lower()
    
    # Find sentences or phrases with category keywords
    sentences = re.split(r'[.!?]', description)
    
    for sent in sentences:
        sent_lower = sent.lower()
        # Check if this sentence matches category patterns
        if category in CATEGORY_PATTERNS:
            for pattern in CATEGORY_PATTERNS[category]:
                if re.search(pattern, sent_lower):
                    returned_text = sent.strip()[:max_length]
                    return returned_text
    
    # Fallback: return first 60 chars of description
    return description[:max_length]


def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description.
    
    Args:
        description: Raw complaint text
    
    Returns:
        dict with keys: category, priority, reason, flag
    """
    # Validation: refuse on blank
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # ========================================================================
    # STEP 1: Severity Keyword Scan (FIRST) → Determine Priority
    # ========================================================================
    priority = "Standard"
    if any(keyword in description_lower for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    
    # ========================================================================
    # STEP 2: Category Assignment (Exact String Matching)
    # ========================================================================
    category_matches = {}
    
    for category, patterns in CATEGORY_PATTERNS.items():
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, description_lower):
                match_count += 1
        
        if match_count > 0:
            category_matches[category] = match_count
    
    # Assign to highest-scoring category
    if category_matches:
        category = max(category_matches, key=category_matches.get)
    else:
        category = "Other"
    
    # ========================================================================
    # STEP 3: Generate Justification (One Sentence + Specific Citation)
    # ========================================================================
    citation = extract_citation(description, category)
    reason = f"Classified as {category} because description mentions '{citation}'"
    
    # ========================================================================
    # STEP 4: Ambiguity Assessment (Genuine multi-category fit)
    # ========================================================================
    flag = ""
    
    # If multiple categories have equal high scores → ambiguous
    if len(category_matches) > 1:
        scores = sorted(category_matches.values(), reverse=True)
        if scores[0] == scores[1]:  # Top two categories tied
            flag = "NEEDS_REVIEW"
    
    # Special case: complaint mentions both flooding AND drain
    if "flood" in description_lower and ("drain" in description_lower or "block" in description_lower):
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
    
    Args:
        input_path: Path to input CSV (test_[city].csv)
        output_path: Path to write results CSV
    
    Processing:
        - Reads input CSV with complaint descriptions
        - Classifies each row independently
        - Writes output CSV with category, priority, reason, flag
        - Does not crash on bad rows; logs and continues
    """
    results = []
    error_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for row_num, row in enumerate(reader, start=2):  # Start=2 to account for header
                try:
                    # Extract description from row
                    description = row.get('description', '').strip()
                    
                    if not description:
                        print(f"⚠ Row {row_num}: Empty description, skipping")
                        error_count += 1
                        continue
                    
                    # Classify this complaint
                    classification = classify_complaint(description)
                    
                    # Prepare output row
                    output_row = {
                        'description': description,
                        'category': classification['category'],
                        'priority': classification['priority'],
                        'reason': classification['reason'],
                        'flag': classification['flag']
                    }
                    
                    results.append(output_row)
                
                except Exception as e:
                    print(f"⚠ Row {row_num}: Error processing — {str(e)}")
                    error_count += 1
                    continue
        
        # Write output CSV
        if results:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['description', 'category', 'priority', 'reason', 'flag']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"✓ Successfully classified {len(results)} complaints")
            if error_count > 0:
                print(f"⚠ {error_count} rows had errors and were skipped")
            print(f"✓ Results written to {output_path}")
        else:
            print("✗ No complaints were successfully classified")
    
    except FileNotFoundError:
        print(f"✗ Input file not found: {input_path}")
        raise
    except Exception as e:
        print(f"✗ Error during batch processing: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
