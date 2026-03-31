"""
UC-0A — Complaint Classifier
Implemented using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import re

# Taxonomy enforcement
APPROVED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agents.md and skills.md specifications.
    
    Args:
        row: Dict with keys complaint_id and description
        
    Returns:
        Dict with keys: complaint_id, category, priority, reason, flag
        Always returns valid dict; never raises exception.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")
    
    # Error handling: empty or too short description
    if not description or len(str(description).strip()) < 3:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    description_text = str(description).strip()
    description_lower = description_text.lower()
    
    # Check for severity keywords (case-insensitive)
    has_severity_keyword = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity_keyword else "Standard"
    
    # Category classification logic
    category = _classify_category(description_lower, description_text)
    
    # Generate reason citing specific words from description
    reason = _generate_reason(category, description_text)
    
    # Determine if flagging needed
    flag = _determine_flag(category, description_lower, has_severity_keyword, reason)
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description_lower: str, description_text: str) -> str:
    """
    Classify description into one of the approved categories.
    Returns category name or "Other" if ambiguous or unmatched.
    """
    # Keyword matching for each category
    category_keywords = {
        "Pothole": ["pothole", "crater", "hole", "pit", "bump", "ditch", "rut"],
        "Flooding": ["flood", "water", "waterlog", "inundation", "drain", "overflow"],
        "Streetlight": ["light", "streetlight", "street lamp", "lamp", "dark", "unlit", "lighting"],
        "Waste": ["garbage", "trash", "waste", "rubbish", "litter", "dump", "filth"],
        "Noise": ["noise", "sound", "loud", "din", "honking", "music", "music"],
        "Road Damage": ["road", "asphalt", "pavement", "cracked", "broken", "damaged"],
        "Heritage Damage": ["heritage", "monument", "historic", "damaged structure", "old building"],
        "Heat Hazard": ["heat", "temperature", "extreme heat", "burning", "thermal"],
        "Drain Blockage": ["drain", "blocked", "clogged", "obstruction", "sewer"],
    }
    
    # Score categories by keyword matches
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in description_lower)
        if score > 0:
            category_scores[category] = score
    
    # If clear winner, return it
    if category_scores:
        top_category = max(category_scores, key=category_scores.get)
        top_score = category_scores[top_category]
        
        # Check for ambiguity (multiple categories with same score)
        tied_categories = [cat for cat, score in category_scores.items() if score == top_score]
        if len(tied_categories) == 1:
            return top_category
    
    return "Other"


def _generate_reason(category: str, description_text: str) -> str:
    """
    Generate a one-sentence reason citing specific words from description.
    """
    description_lower = description_text.lower()
    
    # Extract key phrases from description (up to 2-3 meaningful words)
    words = description_text.split()
    relevant_words = []
    for word in words:
        if len(word) > 3 and word.lower() not in ["the", "that", "this", "with", "from", "have"]:
            relevant_words.append(word)
            if len(relevant_words) >= 3:
                break
    
    cited_words = ", ".join(relevant_words[:2]) if relevant_words else "description text"
    
    if category == "Other":
        return f"Insufficient information to classify: description mentions {cited_words}."
    else:
        return f"Assigned {category}: description mentions {cited_words}."


def _determine_flag(category: str, description_lower: str, has_severity_keyword: bool, reason: str) -> str:
    """
    Determine if NEEDS_REVIEW flag should be set based on ambiguity criteria.
    """
    # Flag if category is "Other" (inherent ambiguity)
    if category == "Other":
        return "NEEDS_REVIEW"
    
    # Flag if description is too vague (very short)
    if len(description_lower) < 20:
        return "NEEDS_REVIEW"
    
    return ""


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint to each row, write results CSV.
    
    Handles errors gracefully: malformed rows, missing files, exceptions.
    Always writes output even if some rows fail.
    """
    rows_processed = 0
    rows_flagged = 0
    
    try:
        # Read input CSV
        rows = []
        try:
            with open(input_path, "r", encoding="utf-8") as infile:
                reader = csv.DictReader(infile)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        rows.append(row)
                    except Exception as e:
                        print(f"Warning: Skipped malformed row {row_num}: {e}", file=sys.stderr)
        except FileNotFoundError:
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        
        # Classify each row
        results = []
        for row in rows:
            try:
                result = classify_complaint(row)
                results.append(result)
                rows_processed += 1
                if result["flag"] == "NEEDS_REVIEW":
                    rows_flagged += 1
            except Exception as e:
                print(f"Warning: Classification error for row {row.get('complaint_id', '?')}: {e}", file=sys.stderr)
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification error",
                    "flag": "NEEDS_REVIEW"
                }
                results.append(result)
                rows_processed += 1
                rows_flagged += 1
        
        # Write output CSV
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error: Could not write output file {output_path}: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Print summary
        print(f"Processed {rows_processed} rows, {rows_flagged} flagged for review, wrote results to {output_path}")
        
    except Exception as e:
        print(f"Unexpected error during batch classification: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
  python classifier.py  # Uses default test_pune.csv
        """
    )
    parser.add_argument("--input", default="../data/city-test-files/test_pune.csv", 
                        help="Path to test_[city].csv (default: test_pune.csv)")
    parser.add_argument("--output", default=None,
                        help="Path to write results CSV (default: results_[city].csv)")
    args = parser.parse_args()
    
    # Auto-generate output filename if not provided
    if args.output is None:
        # Extract city name from input path
        import os
        input_filename = os.path.basename(args.input)
        if input_filename.startswith("test_") and input_filename.endswith(".csv"):
            city = input_filename.replace("test_", "").replace(".csv", "")
            args.output = f"results_{city}.csv"
        else:
            args.output = "results.csv"
    
    batch_classify(args.input, args.output)
