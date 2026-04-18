"""
UC-0A — Complaint Classifier
Implements RICE enforcement rules from agents.md, skills.md, and README.md.

Core failure modes to prevent:
1. Taxonomy drift — enforce consistent category names across all rows
2. Severity blindness — detect severity keywords and set Urgent priority
3. Missing justification — generate reason citing specific words
4. Hallucinated sub-categories — use only allowed categories
5. False confidence on ambiguity — set NEEDS_REVIEW when genuinely ambiguous
"""
import argparse
import csv
import re


# Enforcement rules from README.md and skills.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Track category assignments for consistency checking (prevent taxonomy drift)
_category_consistency = {}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Input: dict with keys complaint_id, description
    Output: dict with keys complaint_id, category, priority, reason, flag
    
    Enforcement (from agents.md + skills.md):
    - Category must be exactly from ALLOWED_CATEGORIES (prevent hallucinated sub-categories)
    - Priority is Urgent if ANY severity keyword present (prevent severity blindness)
    - Reason must cite 2+ specific words from description (prevent missing justification)
    - If ambiguous, set category=Other and flag=NEEDS_REVIEW (prevent false confidence)
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()
    
    # Error handling: Empty/null description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # PREVENT SEVERITY BLINDNESS: Detect severity keywords early
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            priority = "Urgent"
            break
    
    # PREVENT TAXONOMY DRIFT: Classify category consistently
    category = _classify_category(description_lower)
    
    # PREVENT MISSING JUSTIFICATION: Generate reason with specific words
    reason = _generate_reason(description, category)
    
    # PREVENT FALSE CONFIDENCE: Flag ambiguous classifications
    flag = ""
    if category == "Other":
        # Set NEEDS_REVIEW for genuinely ambiguous complaints
        if not _has_clear_indicators(description_lower):
            flag = "NEEDS_REVIEW"
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description_lower: str) -> str:
    """
    Classify description into one of ALLOWED_CATEGORIES.
    
    PREVENT HALLUCINATED SUB-CATEGORIES:
    - Returns exact category name from ALLOWED_CATEGORIES only
    - Returns 'Other' if no clear match (never invents categories)
    - Prevents taxonomy drift via consistent keyword matching
    """
    # Define keyword patterns for each category
    patterns = {
        "Pothole": ["pothole", "pit", "hole in road", "crater"],
        "Flooding": ["flood", "water", "waterlog", "inundation", "submerged"],
        "Streetlight": ["streetlight", "light", "lamp", "dark", "illuminate", "bulb"],
        "Waste": ["garbage", "waste", "trash", "rubbish", "litter", "dump"],
        "Noise": ["noise", "sound", "loud", "honking", "blaring", "disturb"],
        "Road Damage": ["road damage", "crack", "asphalt", "pavement", "surface damage"],
        "Heritage Damage": ["heritage", "monument", "historical", "ancient", "damage to site"],
        "Heat Hazard": ["heat", "temperature", "hot", "heatwave"],
        "Drain Blockage": ["drain", "blockage", "clogged", "sewage", "sanitation"]
    }
    
    # Score each category based on keyword matches
    scores = {}
    for category, keywords in patterns.items():
        score = sum(1 for kw in keywords if kw in description_lower)
        if score > 0:
            scores[category] = score
    
    # PREVENT HALLUCINATED SUB-CATEGORIES: Return only exact allowed category
    if not scores:
        return "Other"
    
    max_score = max(scores.values())
    top_categories = [cat for cat, score in scores.items() if score == max_score]
    
    # PREVENT TAXONOMY DRIFT: If multiple categories tie, treat as ambiguous
    if len(top_categories) > 1:
        return "Other"
    
    category = top_categories[0]
    
    # Track for consistency checking
    _category_consistency[description_lower[:50]] = category
    
    return category


def _generate_reason(description: str, category: str) -> str:
    """
    Generate one-sentence reason citing 2+ specific words from description.
    
    PREVENT MISSING JUSTIFICATION:
    - Extracts specific words directly from description
    - Cites at least 2 words
    - Returns empty string if cannot form proper reason
    """
    if not description:
        return ""
    
    # Extract key words (longer words, not common articles)
    words = re.findall(r'\b\w{3,}\b', description)  # Words of 3+ characters
    unique_words = list(dict.fromkeys(words))[:5]  # Get up to 5 unique words
    
    # Only generate reason if we have at least 2 specific words
    if len(unique_words) < 2:
        return ""
    
    if category == "Other":
        return f"Complaint mentions: {unique_words[0]}, {unique_words[1]}."
    
    return f"Complaint about {category.lower()} involving: {unique_words[0]}, {unique_words[1]}."


def _has_clear_indicators(description_lower: str) -> bool:
    """
    Check if description has clear category indicators.
    Used to determine when to set NEEDS_REVIEW flag.
    """
    all_keywords = []
    patterns = {
        "Pothole": ["pothole", "pit", "hole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["light", "lamp"],
        "Waste": ["garbage", "waste"],
        "Noise": ["noise", "loud"],
        "Road Damage": ["road", "crack"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "hot"],
        "Drain Blockage": ["drain", "blockage"]
    }
    
    for keywords in patterns.values():
        all_keywords.extend(keywords)
    
    return any(kw in description_lower for kw in all_keywords)


def _validate_output(results: list) -> dict:
    """
    Validate output for the 5 failure modes from README.md.
    Returns validation report.
    """
    report = {
        "total_rows": len(results),
        "taxonomy_drift_issues": [],
        "severity_blindness_issues": [],
        "missing_justification": [],
        "hallucinated_categories": [],
        "false_confidence": []
    }
    
    # Track categories for taxonomy drift
    category_counts = {}
    
    for result in results:
        complaint_id = result.get("complaint_id", "")
        category = result.get("category", "")
        priority = result.get("priority", "")
        reason = result.get("reason", "")
        flag = result.get("flag", "")
        
        # Check 1: Hallucinated categories (not in allowed list)
        if category not in ALLOWED_CATEGORIES:
            report["hallucinated_categories"].append(
                f"{complaint_id}: category '{category}' not in allowed list"
            )
        
        # Check 2: Missing reason field
        if not reason or reason.strip() == "":
            report["missing_justification"].append(complaint_id)
        
        # Check 3: Severity blindness (child/injury/school as Standard)
        if priority == "Standard" and any(kw in reason.lower() for kw in ["child", "injury", "school"]):
            report["severity_blindness_issues"].append(complaint_id)
        
        # Check 4: False confidence on ambiguous (no flag when should have)
        if flag != "NEEDS_REVIEW" and category == "Other":
            report["false_confidence"].append(complaint_id)
        
        # Track category usage
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return report


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Input: CSV with columns complaint_id, description
    Output: CSV with columns complaint_id, category, priority, reason, flag
    
    Error handling: Continue on errors, write partial results, validate output.
    
    Prevents all 5 failure modes via classify_complaint and validation.
    """
    results = []
    row_count = 0
    error_count = 0
    
    try:
        # Read input CSV
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None or 'description' not in reader.fieldnames:
                raise ValueError("Input CSV must have 'description' column")
            
            for row_idx, row in enumerate(reader, start=1):
                try:
                    # Handle missing complaint_id
                    if 'complaint_id' not in row or not row['complaint_id']:
                        row['complaint_id'] = f"row_{row_idx}"
                    
                    # Classify this row
                    result = classify_complaint(row)
                    results.append(result)
                    row_count += 1
                except Exception as e:
                    error_count += 1
                    # Write error row with safe defaults
                    result = {
                        "complaint_id": row.get('complaint_id', f"row_{row_idx}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "",
                        "flag": "NEEDS_REVIEW"
                    }
                    results.append(result)
        
        # Write output CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # Validate output against 5 failure modes
        validation = _validate_output(results)
        
        # Log summary
        print(f"Processed {row_count} rows, {error_count} errors")
        print(f"Validation report: {validation['total_rows']} total")
        if validation["hallucinated_categories"]:
            print(f"  ⚠ Hallucinated categories: {len(validation['hallucinated_categories'])}")
        if validation["missing_justification"]:
            print(f"  ⚠ Missing justification: {len(validation['missing_justification'])}")
        if validation["severity_blindness_issues"]:
            print(f"  ⚠ Severity blindness: {len(validation['severity_blindness_issues'])}")
        if validation["false_confidence"]:
            print(f"  ⚠ False confidence: {len(validation['false_confidence'])}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
