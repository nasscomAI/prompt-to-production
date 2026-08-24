"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and ambiguity flag.
"""
import argparse
import csv
import re

# Allowed categories (exact strings only)
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category detection patterns (map keywords to categories)
CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "pit", "crater", "hole in road", "tyre damage"],
    "Flooding": ["flood", "water", "submerged", "stranded", "waterlogged"],
    "Streetlight": ["light", "streetlight", "bulb", "sparking", "dark", "flickering"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumped", "rubbish"],
    "Noise": ["noise", "music", "sound", "loud", "disturbance"],
    "Road Damage": ["cracked", "sinking", "surface damage", "road condition", "damaged"],
    "Heritage Damage": ["heritage", "historic", "old city", "monument"],
    "Heat Hazard": ["heat", "temperature", "burn", "hot"],
    "Drain Blockage": ["drain", "blockage", "clogged", "blocked"],
}


def extract_severity_level(description: str) -> bool:
    """Check if description contains any severity keyword that triggers Urgent."""
    if not description:
        return False
    desc_lower = description.lower()
    return any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS)


def detect_category(description: str) -> tuple[str, str]:
    """
    Detect category from description. Returns (category, reason).
    reason: one-sentence justification citing specific words from description.
    """
    if not description:
        return "Other", "No description provided."
    
    desc_lower = description.lower()
    scores = {}
    
    # Score each category based on pattern matches
    for category, keywords in CATEGORY_PATTERNS.items():
        score = 0
        matched_keywords = []
        for keyword in keywords:
            if keyword in desc_lower:
                score += 1
                matched_keywords.append(keyword)
        if score > 0:
            scores[category] = (score, matched_keywords)
    
    # Find best match
    if scores:
        best_category = max(scores, key=lambda x: scores[x][0])
        matched_kw = scores[best_category][1]
        # Build reason citing specific words from description
        reason = f"Complaint describes {best_category.lower()} issue with keywords: {', '.join(matched_kw[:3])}."
        return best_category, reason
    
    # No clear match — ambiguous
    return "Other", "Complaint does not clearly match any category."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input: dict with complaint_id and description (and optionally other fields).
    Output: dict with complaint_id, category, priority, reason, flag.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Detect category and reason
    category, reason = detect_category(description)
    
    # Determine priority: Urgent if severity keywords present, else Standard
    priority = "Urgent" if extract_severity_level(description) else "Standard"
    
    # Flag if category is Other (genuinely ambiguous)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
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
    Preserves all input columns and adds: category, priority, reason, flag.
    """
    classified_rows = []
    error_count = 0
    success_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            input_fieldnames = reader.fieldnames
            
            for row_idx, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                try:
                    classification = classify_complaint(row)
                    # Merge input row with classification
                    output_row = {**row, **classification}
                    classified_rows.append(output_row)
                    success_count += 1
                except Exception as e:
                    print(f"Error processing row {row_idx}: {e}", file=__import__('sys').stderr)
                    error_count += 1
                    continue
        
        # Write output CSV with all columns
        output_fieldnames = input_fieldnames + ["category", "priority", "reason", "flag"]
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
        
        print(f"Successfully classified {success_count} rows. Errors: {error_count}")
        
    except IOError as e:
        print(f"File error: {e}", file=__import__('sys').stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
