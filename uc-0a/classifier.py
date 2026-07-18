"""
UC-0A — Complaint Classifier
Enforces strict taxonomy consistency, severity detection, and evidence citation.
"""
import argparse
import csv
import sys
from typing import Dict, Optional

# Enforcement: Allowed categories (exact strings only)
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

# Enforcement: Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

# Category detection rules based on keywords in description
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole"],
    "Flooding": ["flood", "flooded", "flooded", "waterlog", "inundated", "submerged"],
    "Streetlight": ["streetlight", "street light", "light", "lamppost", "bulb", "lighting"],
    "Waste": ["waste", "garbage", "rubbish", "trash", "litter", "debris", "dumped"],
    "Noise": ["noise", "sound", "music", "loud", "blaring", "horn"],
    "Road Damage": ["road", "crack", "sinking", "surface", "asphalt", "pavement"],
    "Heritage Damage": ["heritage", "historic", "monument", "temple", "old"],
    "Heat Hazard": ["heat", "temperature", "burn", "scorch"],
    "Drain Blockage": ["drain", "blocked", "blockage", "clogged"],
}

def extract_evidence(description: str) -> str:
    """Extract first clause or key phrase from description for reason field."""
    # Take first sentence or first 50 chars
    sentences = description.split(".")
    first_part = sentences[0].strip()
    if len(first_part) > 100:
        first_part = first_part[:100] + "..."
    return first_part

def detect_severity(description: str) -> bool:
    """Check if description contains any severity keywords."""
    description_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            return True
    return False

def classify_category(description: str) -> tuple:
    """
    Classify complaint into allowed category.
    Returns: (category, flag)
    - category: one of ALLOWED_CATEGORIES
    - flag: NEEDS_REVIEW if ambiguous, else ""
    """
    description_lower = description.lower()
    scores = {}
    
    # Score each category based on keyword matches
    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in description_lower)
        if matches > 0:
            scores[category] = matches
    
    # If no clear match, return Other with flag
    if not scores:
        return "Other", "NEEDS_REVIEW"
    
    # If multiple categories have same high score, flag for review
    max_score = max(scores.values())
    candidates = [cat for cat, score in scores.items() if score == max_score]
    
    if len(candidates) > 1:
        # Multiple strong candidates - ambiguous
        best_category = candidates[0]
        return best_category, "NEEDS_REVIEW"
    
    # Single clear winner
    return candidates[0], ""

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforcement rules:
    1. Category must be exactly one of the allowed values
    2. Priority is Urgent if ANY severity keyword present
    3. Reason must cite specific words from description
    4. Flag set to NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")
    
    # Handle missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Unable to parse complaint description",
            "flag": "NEEDS_REVIEW"
        }
    
    # Detect severity and determine priority
    has_severity = detect_severity(description)
    priority = "Urgent" if has_severity else "Standard"
    
    # Classify into category
    category, ambiguity_flag = classify_category(description)
    
    # Extract evidence from description for reason
    evidence = extract_evidence(description)
    
    # Build reason: cite evidence + severity if present
    if has_severity:
        # Find which severity keyword triggered it
        severity_found = None
        for keyword in SEVERITY_KEYWORDS:
            if keyword in description.lower():
                severity_found = keyword
                break
        reason = f"{evidence} (severity: {severity_found})"
    else:
        reason = evidence
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": ambiguity_flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Enforcement:
    - Must validate all output categories against ALLOWED_CATEGORIES
    - Must not crash on bad rows
    - Must produce output even if some rows fail
    """
    rows = []
    error_count = 0
    
    # Read input CSV
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"ERROR: Failed to read input file: {e}", file=sys.stderr)
        raise
    
    # Classify each row
    results = []
    for i, row in enumerate(rows):
        try:
            classified = classify_complaint(row)
            
            # Validation: ensure category is in allowed list
            if classified["category"] not in ALLOWED_CATEGORIES:
                print(f"WARNING: Row {i+1} - Invalid category '{classified['category']}', setting to Other", file=sys.stderr)
                classified["category"] = "Other"
                classified["flag"] = "NEEDS_REVIEW"
            
            results.append(classified)
        except Exception as e:
            print(f"WARNING: Row {i+1} failed to classify: {e}", file=sys.stderr)
            error_count += 1
            # Still add to results with safe defaults
            results.append({
                "complaint_id": row.get("complaint_id", f"ERROR-{i+1}"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification error: {str(e)[:50]}",
                "flag": "NEEDS_REVIEW"
            })
    
    # Write output CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except IOError as e:
        print(f"ERROR: Failed to write output file: {e}", file=sys.stderr)
        raise
    
    if error_count > 0:
        print(f"Warnings: {error_count} row(s) had classification errors, marked with flag=NEEDS_REVIEW", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"✓ Done. Results written to {args.output}")
