"""
UC-0A — Complaint Classifier
Classifies citizen complaints into categories with priority levels based on severity keywords.
"""
import argparse
import csv
import re
import sys
from typing import Dict, Any, Optional

# Classification schema - exact taxonomy
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category patterns - map description patterns to categories
CATEGORY_PATTERNS = {
    "Pothole": r"\b(pothole|crater|pit|hole.*road|road.*pit|tyre.*damage|wheel.*damage)\b",
    "Flooding": r"\b(flood|water.*accumulation|knee-deep|submerged|inundated|waterlogged|water.*logged|flooded)\b",
    "Streetlight": r"\b(streetlight|street.*light|light.*out|lights?s?\b|lamp.*out|electrical.*hazard|sparking|flickering.*spark)\b",
    "Waste": r"\b(garbage|waste|rubbish|trash|debris|bin|litter|dump|refuse|dead.*animal)\b",
    "Noise": r"\b(noise|music|sound|loud|blaring|disturbance|nuisance)\b",
    "Road Damage": r"\b(road.*cracked|sinking|cracks?|surface.*damage|utility.*work|manhole.*missing)\b",
    "Heritage Damage": r"\b(heritage|historic|old.*city|rasta.*peth|monument|preserved)\b",
    "Heat Hazard": r"\b(heat|temperature|extreme.*heat|heatwave|summer)\b",
    "Drain Blockage": r"\b(drain.*block|clogged.*drain|drainage.*problem|stagnant|sewage)\b",
}


def extract_evidence(description: str, category: str) -> Optional[str]:
    """Extract specific words from description that triggered the category classification."""
    if not description:
        return None
    pattern = CATEGORY_PATTERNS.get(category)
    if pattern:
        matches = re.findall(pattern, description, re.IGNORECASE)
        if matches:
            # Return first matched phrase
            words = [m for match_tuple in matches for m in (match_tuple if isinstance(match_tuple, tuple) else (match_tuple,))]
            if words:
                return words[0]
    return None


def classify_complaint(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a single complaint row.
    
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # Result dict - copy all input fields
    result = dict(row)
    
    # Handle empty/null description
    if not description:
        result["category"] = "Other"
        result["priority"] = "Standard"
        result["reason"] = "No description provided."
        result["flag"] = "NEEDS_REVIEW"
        return result
    
    description_lower = description.lower()
    
    # Check for severity keywords to determine priority
    has_severity = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"
    
    # Classify into category - find first matching pattern
    category = "Other"
    evidence = None
    
    for cat, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, description, re.IGNORECASE):
            category = cat
            evidence = extract_evidence(description, cat)
            break
    
    # Build reason field - cite specific evidence
    if evidence:
        reason = f"Classified from key terms: '{evidence}'"
    elif category == "Other":
        reason = f"Description does not match specific categories."
    else:
        reason = f"Matched {category} criteria."
    
    # Set flag if needed - only for genuinely ambiguous cases
    flag = ""
    
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    Continues on individual row failures; flags failures for review.
    """
    try:
        # Read input file
        rows = []
        fieldnames = []
        
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
        
        if not rows:
            print(f"Warning: Input file {input_path} is empty.")
            return
        
        # Classify each row
        classified_rows = []
        for i, row in enumerate(rows):
            try:
                classified_row = classify_complaint(row)
                classified_rows.append(classified_row)
            except Exception as e:
                print(f"Error processing row {i+1} ({row.get('complaint_id', 'UNKNOWN')}): {e}")
                # Add row with error flag
                row["category"] = "Other"
                row["priority"] = "Standard"
                row["reason"] = f"Error during classification: {str(e)}"
                row["flag"] = "NEEDS_REVIEW"
                classified_rows.append(row)
        
        # Write output file - include new columns
        output_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
        
        print(f"Successfully classified {len(classified_rows)} complaints.")
        print(f"Results written to {output_path}")
        
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
