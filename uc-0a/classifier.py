"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from pathlib import Path

# Allowed categories — exact strings only, no synonyms or variations
ALLOWED_CATEGORIES = [
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
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", 
    "ambulance", "fire", "hazard", "fell", "collapse",
    "dead"
]

# Category keywords for matching descriptions to categories
CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "potholes", "hole", "tyre damage", "pit"],
    "Flooding": ["flood", "flooded", "flooding", "stranded", "inaccessible"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "dark at night"],
    "Waste": ["garbage", "waste", "dumped", "bin", "litter", "renovation debris"],
    "Noise": ["noise", "music", "loud", "past midnight", "disturbance", "band", "festival"],
    "Road Damage": ["road surface", "cracked", "sinking", "road", "tiles broken", "tiles upturned"],
    "Heritage Damage": ["heritage", "historic", "old city"],
    "Heat Hazard": ["heat", "hot", "temperature", "heatwave"],
    "Drain Blockage": ["drain", "blocked", "drainage", "manhole cover missing"],
    "Other": []
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Classification rules from agents.md and skills.md:
    - category must be an exact string from ALLOWED_CATEGORIES
    - priority is Urgent if severity keywords present, else Standard or Low
    - reason must cite specific words verbatim from description
    - flag is set only when category genuinely cannot be determined
    """
    complaint_id = row.get("complaint_id", "unknown")
    description = row.get("description", "").lower()
    
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    # Determine category based on keyword matching
    category = "Other"
    matched_keywords = []
    category_scores = {}
    
    for cat, keywords in CATEGORY_PATTERNS.items():
        if cat == "Other":
            continue
        score = 0
        cat_matched = []
        for keyword in keywords:
            if keyword.lower() in description:
                score += 1
                cat_matched.append(keyword)
        if score > 0:
            category_scores[cat] = (score, cat_matched)
    
    # Select category with highest match score
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1][0])
        category = best_category[0]
        matched_keywords = best_category[1][1]
    
    # Determine priority based on severity keywords
    priority = "Standard"
    severity_matched = []
    
    for keyword in SEVERITY_KEYWORDS:
        # Use word boundary matching for better accuracy
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, description, re.IGNORECASE):
            severity_matched.append(keyword)
    
    if severity_matched:
        priority = "Urgent"
    
    # Generate reason citing specific words from description
    all_cited = matched_keywords + severity_matched
    if all_cited:
        # Remove duplicates while preserving order
        seen = set()
        unique_cited = []
        for word in all_cited:
            if word.lower() not in seen:
                seen.add(word.lower())
                unique_cited.append(word)
        reason = f"Description contains: {', '.join(unique_cited)}"
    else:
        reason = "General complaint, no specific category keywords detected"
        # Set flag if we couldn't determine category clearly
        if category == "Other":
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": priority,
                "reason": reason,
                "flag": "NEEDS_REVIEW"
            }
    
    # Set flag only when genuinely ambiguous
    flag = ""
    if category == "Other" and not matched_keywords:
        flag = "NEEDS_REVIEW"
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Error handling as per skills.md:
    - Raise error with specific message if input file is missing or malformed
    - Log warning for any individual row that requires NEEDS_REVIEW flag
    - Produce output even if some rows fail (don't crash on bad rows)
    """
    input_file = Path(input_path)
    
    # Check if input file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Read input CSV
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except csv.Error as e:
        raise ValueError(f"Malformed CSV file: {input_path}. Error: {e}")
    except Exception as e:
        raise ValueError(f"Cannot read input file: {input_path}. Error: {e}")
    
    if not rows:
        raise ValueError(f"Input file is empty: {input_path}")
    
    # Classify each row
    results = []
    warning_count = 0
    
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
            
            # Log warning for rows requiring review
            if result.get("flag") == "NEEDS_REVIEW":
                warning_count += 1
                print(f"Warning: Row {result['complaint_id']} flagged for review")
        except Exception as e:
            # Don't crash on bad rows — log error and continue
            complaint_id = row.get("complaint_id", "unknown")
            print(f"Warning: Failed to classify row {complaint_id}: {e}")
            results.append({
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification failed: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            warning_count += 1
    
    # Write output CSV
    output_file = Path(output_path)
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        raise ValueError(f"Cannot write output file: {output_path}. Error: {e}")
    
    print(f"Classified {len(results)} rows. {warning_count} rows flagged for review.")
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
