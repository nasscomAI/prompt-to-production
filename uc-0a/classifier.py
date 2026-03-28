"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import re

# Allowed categories from enforcement rules
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Keyword to category mapping for classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "pit"],
    "Flooding": ["flood", "flooded", "water", "stranded", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "light pole", "street lamp"],
    "Waste": ["waste", "garbage", "trash", "litter", "dirty"],
    "Noise": ["noise", "sound", "loud", "喇叭", "喧哗"],
    "Road Damage": ["road damage", "road broken", "road crack", "road collapse", "road sink", "surface cracked", "sinking"],
    "Heritage Damage": ["heritage", "monument", "historical"],
    "Heat Hazard": ["heat", "hot", "temperature", "heatwave", "sun"],
    "Drain Blockage": ["drain", "drainage", "sewer", "gutter", "blocked"],
}

# Related categories that shouldn't appear together without manual review
RELATED_CATEGORIES = [
    {"Flooding", "Drain Blockage"},
    {"Flooding", "Road Damage"},
    {"Road Damage", "Pothole"},
]


def _contains_severity_keyword(description: str) -> bool:
    """Check if description contains any severity keyword (case-insensitive)."""
    desc_lower = description.lower()
    return any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS)


def _determine_category(description: str) -> tuple[str, bool]:
    """
    Determine the category based on description content.
    Returns: (category, is_ambiguous)
    """
    desc_lower = description.lower()
    
    # Check for severity keywords that might indicate urgent issues
    severity_matches = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    
    # Map to categories
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            category_scores[category] = score
    
    if not category_scores:
        return "Other", True  # Ambiguous - no category match
    
    # Get highest scoring category
    best_category = max(category_scores, key=category_scores.get)
    max_score = category_scores[best_category]
    
    # Check for ambiguity: tied categories, second-best is very close, or related categories present
    sorted_scores = sorted(category_scores.values(), reverse=True)
    tied_categories = [c for c, s in category_scores.items() if s == max_score]
    
    # Check if related categories are both present
    matched_cats = set(category_scores.keys())
    has_related = False
    for rel_pair in RELATED_CATEGORIES:
        if rel_pair.issubset(matched_cats):
            has_related = True
            break
    
    is_ambiguous = len(tied_categories) > 1 or (len(sorted_scores) > 1 and sorted_scores[0] == sorted_scores[1]) or has_related
    
    return best_category, is_ambiguous


def _determine_priority(description: str, category: str) -> str:
    """
    Determine priority based on severity keywords.
    Urgent if severity keywords present, otherwise Standard or Low based on category.
    """
    if _contains_severity_keyword(description):
        return "Urgent"
    
    # Low priority categories
    if category in ["Streetlight", "Waste"]:
        return "Low"
    
    return "Standard"


def _extract_reason(description: str, category: str) -> str:
    """
    Extract specific words from description to justify the classification.
    Returns a single sentence citing verbatim words from the description.
    """
    desc_lower = description.lower()
    
    # Find matching keywords from the determined category
    category_keywords = CATEGORY_KEYWORDS.get(category, [])
    matched_words = []
    
    for keyword in category_keywords:
        # Find the keyword in original description (case-insensitive search)
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        match = pattern.search(description)
        if match:
            # Extract the exact text from description
            matched_words.append(match.group(0))
    
    # Also check for severity keywords
    severity_matches = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            match = pattern.search(description)
            if match:
                severity_matches.append(match.group(0))
    
    # Build reason sentence
    all_matched = matched_words[:2]  # Take up to 2 category words
    all_matched.extend(severity_matches[:2])  # Add severity words if any
    
    if all_matched:
        return f"Classification based on presence of: {', '.join(set(all_matched))}."
    
    # Fallback: cite first 5 words of description
    words = description.split()[:5]
    if words:
        return f"Classification based on description mentioning: {' '.join(words)}."
    
    return "No specific keywords found in description."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Input: dict with keys including 'description' (required) and 'location' (optional)
    
    Returns: dict with keys:
        - complaint_id: from input row
        - category: one of the 10 allowed values
        - priority: Urgent, Standard, or Low
        - reason: sentence citing specific words from description
        - flag: NEEDS_REVIEW if ambiguous, empty string otherwise
    
    Error handling:
        - If description is empty or contains no classifiable content:
          category=Other, flag=NEEDS_REVIEW
        - If severity keywords present: force priority=Urgent
    """
    description = row.get("description", "").strip()
    
    # Error handling: empty or no content
    if not description or len(description) < 5:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Description empty or too short to classify.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Determine category and ambiguity
    category, is_ambiguous = _determine_category(description)
    priority = _determine_priority(description, category)
    reason = _extract_reason(description, category)
    
    # Force Urgent if severity keywords present (enforcement rule)
    if _contains_severity_keyword(description):
        priority = "Urgent"
    
    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Input: 
        - input_path: Path to input CSV with complaint data
        - output_path: Path to write classified results
    
    Output: CSV file at output_path containing all original columns plus:
        - category, priority, reason, flag (added by classify_complaint)
    
    Error handling:
        - If input file cannot be read: raise FileNotFoundError with filename
        - If a row cannot be classified: log row number, apply default classification
          (category: Other, priority: Low, flag: NEEDS_REVIEW), continue processing
        - Do not stop processing on individual row failures
    """
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    results = []
    
    for idx, row in enumerate(rows):
        try:
            classified = classify_complaint(row)
            # Merge original row with classification results
            result_row = {**row, **classified}
            results.append(result_row)
        except Exception as e:
            # Log the error and apply default classification
            print(f"Warning: Row {idx + 1} could not be classified: {e}. Applying default.")
            default_classification = {
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {str(e)}",
                "flag": "NEEDS_REVIEW"
            }
            result_row = {**row, **default_classification}
            results.append(result_row)
    
    # Write output CSV
    if results:
        fieldnames = list(results[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
