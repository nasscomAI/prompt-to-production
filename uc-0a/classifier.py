"""
UC-0A — Complaint Classifier
Implements agents.md and skills.md enforcement rules for complaint classification.
"""
import argparse
import csv
import os
import re

# Enforcement constants from README.md and agents.md
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

PRIORITY_LEVELS = {"Urgent", "Standard", "Low"}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using agents.md and skills.md rules.
    Returns: dict with keys: category, priority, reason, flag
    
    Enforcement:
    - Category: exact match from ALLOWED_CATEGORIES
    - Priority: Urgent if severity keywords present, else Standard/Low
    - Reason: single sentence citing description words
    - Flag: NEEDS_REVIEW if ambiguous, else empty
    """
    description = row.get("description", "").strip()
    
    # Error handling: empty description
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Check for severity keywords (Urgent priority)
    has_severity = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"
    
    # Classify category based on description patterns
    category, confidence = _infer_category(description_lower)
    
    # Generate reason citing specific words from description
    reason = _generate_reason(description, category, description_lower)
    
    # Set flag for ambiguous cases
    flag = "NEEDS_REVIEW" if not confidence else ""
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _infer_category(description_lower: str) -> tuple:
    """
    Infer category from description text.
    Returns: (category, is_confident)
    """
    # Define keyword patterns for each category
    patterns = {
        "Pothole": ["pothole", "pit", "crater", "hole in road", "broken road"],
        "Flooding": ["flood", "water", "waterlog", "inundat", "stagnant water"],
        "Streetlight": ["light", "street light", "lamp", "dark", "illuminat"],
        "Waste": ["waste", "garbage", "trash", "dump", "litter", "debris"],
        "Noise": ["noise", "loud", "sound", "music", "honking", "construction sound"],
        "Road Damage": ["road", "asphalt", "pavement", "surface", "crack", "roughness"],
        "Heritage Damage": ["heritage", "monument", "historic", "structure damage", "building damage"],
        "Heat Hazard": ["heat", "temperature", "hot", "weather"],
        "Drain Blockage": ["drain", "gutter", "blockage", "clog", "sewage", "overflow"],
    }
    
    # Check matches for each category
    matches = {}
    for category, keywords in patterns.items():
        match_count = sum(1 for kw in keywords if kw in description_lower)
        if match_count > 0:
            matches[category] = match_count
    
    if not matches:
        return "Other", False
    
    # Most specific match wins; ambiguous if tie
    best_category = max(matches, key=matches.get)
    best_count = matches[best_category]
    other_counts = [count for cat, count in matches.items() if cat != best_category]
    
    is_confident = not (other_counts and max(other_counts) == best_count)
    
    return best_category, is_confident


def _generate_reason(original_description: str, category: str, description_lower: str) -> str:
    """
    Generate a reason sentence citing specific words from description.
    """
    if category == "Other":
        return f"Complaint does not clearly match any standard category."
    
    # Find first instance of category-relevant keywords to cite in reason
    category_keywords = {
        "Pothole": ["pothole", "pit", "hole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["light", "lamp"],
        "Waste": ["waste", "garbage", "trash"],
        "Noise": ["noise", "loud"],
        "Road Damage": ["road", "pavement", "crack"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "hot"],
        "Drain Blockage": ["drain", "blockage"],
    }
    
    keywords = category_keywords.get(category, [])
    cited_word = None
    for kw in keywords:
        if kw in description_lower:
            # Find original case version
            for word in original_description.split():
                if kw in word.lower():
                    cited_word = word
                    break
            if cited_word:
                break
    
    if cited_word:
        return f"Classified as {category} based on mention of '{cited_word}' in description."
    else:
        return f"Classified as {category} based on complaint context."


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles errors gracefully: flags nulls, does not crash on bad rows.
    """
    # Error handling: input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    skipped_rows = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                raise ValueError("Input CSV must have a 'description' column")
            
            for row_idx, row in enumerate(reader, start=2):  # start=2 for header
                try:
                    if not row.get("description", "").strip():
                        skipped_rows.append((row_idx, "Empty description"))
                        continue
                    
                    # Classify this row
                    classification = classify_complaint(row)
                    
                    # Merge classification results with original row
                    output_row = {**row, **classification}
                    results.append(output_row)
                    
                except Exception as e:
                    # Error handling: malformed rows get flagged
                    results.append({
                        **row,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error during classification: {str(e)[:50]}",
                        "flag": "NEEDS_REVIEW"
                    })
        
        # Write output CSV
        if results:
            fieldnames = list(results[0].keys())
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        # Log summary
        print(f"Classified {len(results)} rows successfully")
        if skipped_rows:
            print(f"Skipped {len(skipped_rows)} rows with empty descriptions")
    
    except Exception as e:
        raise Exception(f"Error processing CSV: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
