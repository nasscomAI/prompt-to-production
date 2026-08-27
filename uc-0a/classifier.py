"""
UC-0A — Complaint Classifier
Builds classification logic based on RICE principles from agents.md and skills.md.
"""
import argparse
import csv
import re

# Allowed categories - exact strings only
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Keyword to category mapping for classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "tyre damage", "deep pothole", "pothole 60cm"],
    "Flooding": ["flood", "flooded", "floods", "stranded", "underpass flooded", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "lights out", "lights flickering", "flickering"],
    "Waste": ["garbage", "waste", "overflowing", "dumped", "bulk waste", "dead animal", "bin"],
    "Noise": ["noise", "music", "midnight", "wedding venue", "loud"],
    "Road Damage": ["road surface", "cracked", "sinking", "road damage", "tiles broken", "footpath"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave", "extreme heat", "temperature", "hot"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drainage"],
}

# Ambiguous terms that should trigger NEEDS_REVIEW
AMBIGUOUS_TERMS = ["unknown", "unclear", "not sure", "possibly", "maybe", "might be"]


def _contains_severity_keyword(text: str) -> bool:
    """Check if text contains any severity keyword."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SEVERITY_KEYWORDS)


def _extract_quoted_words(text: str, max_words: int = 3) -> list:
    """Extract specific words/phrases from description that support the classification."""
    text_lower = text.lower()
    found = []
    
    # Find words that match category keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found.append(keyword)
                break
    
    # Find severity keywords
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    
    # Return unique found words (max 3)
    return list(dict.fromkeys(found))[:max_words]


def _determine_priority(description: str) -> str:
    """Determine priority based on severity keywords."""
    if _contains_severity_keyword(description):
        return "Urgent"
    return "Standard"


def _classify_category(description: str) -> tuple:
    """
    Classify the complaint into a category.
    Returns: (category, needs_review)
    """
    text_lower = description.lower()
    
    # Check for each category based on keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Check for ambiguity
                if any(term in text_lower for term in AMBIGUOUS_TERMS):
                    return category, True
                return category, False
    
    # Check for severity indicators that might help classify
    if _contains_severity_keyword(text_lower):
        # Try to infer from severity context
        if "fell" in text_lower or "injury" in text_lower:
            if "road" in text_lower or "footpath" in text_lower or "tiles" in text_lower:
                return "Road Damage", False
    
    # Cannot determine - return Other with NEEDS_REVIEW
    return "Other", True


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    RICE Enforcement Rules:
    - Category must be exactly one of the allowed values
    - Priority must be Urgent if description contains severity keywords
    - Reason must cite specific words from description
    - Flag NEEDS_REVIEW when category cannot be determined
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")
    
    # Handle null/empty descriptions
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; defaulting to Other category.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Classify category
    category, needs_review = _classify_category(description)
    
    # Determine priority
    priority = _determine_priority(description)
    
    # Extract quoted words for reason
    cited_words = _extract_quoted_words(description)
    
    # Build reason sentence
    if cited_words:
        reason = f"Classified as {category} based on presence of: {', '.join(cited_words)}."
    else:
        reason = f"Classified as {category} based on description content."
    
    # Set flag
    flag = "NEEDS_REVIEW" if needs_review else ""
    
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
    
    Error handling:
    - Skips rows with missing required fields
    - Continues processing even if individual rows fail
    - Produces output file even if some rows are skipped
    """
    results = []
    skipped_rows = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Validate required columns
            if reader.fieldnames is None:
                raise ValueError("Input CSV has no headers")
            
            required_cols = ["complaint_id", "description"]
            missing_cols = [col for col in required_cols if col not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Log error but continue processing
                    print(f"Warning: Failed to classify row {row_num} ({row.get('complaint_id', 'UNKNOWN')}): {e}")
                    skipped_rows += 1
                    # Add error result for tracking
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_{row_num}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed: {str(e)[:50]}",
                        "flag": "NEEDS_REVIEW"
                    })
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to read input CSV: {e}")
    
    # Write output CSV
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    except Exception as e:
        raise RuntimeError(f"Failed to write output CSV: {e}")
    
    # Report summary
    total_rows = len(results)
    print(f"Processed {total_rows} rows. Skipped: {skipped_rows}.")
    if skipped_rows > 0:
        print(f"Warning: {skipped_rows} row(s) had classification errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
