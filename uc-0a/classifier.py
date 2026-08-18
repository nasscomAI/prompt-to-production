#!/usr/bin/env python3
"""
UC-0A Complaint Classifier

Enforces exact taxonomy, priority rules, severity keyword detection, and ambiguity flagging.
Implements the classify_complaint and batch_classify skills with full error handling.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Tuple


# Enforcement: Exact allowed categories
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

# Enforcement: Exact allowed priorities
ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

# Enforcement: Severity keywords that must trigger Urgent
SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
}


def classify_complaint(complaint_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Skill: classify_complaint
    Classifies a single complaint row into exact category, priority, reason, and ambiguity flag.

    Args:
        complaint_dict: Dict with 'description' field containing complaint text

    Returns:
        Dict with 'category', 'priority', 'reason', 'flag' fields

    Raises:
        ValueError: If input is invalid or violates enforcement rules
    """
    if "description" not in complaint_dict:
        raise ValueError("Input must contain 'description' field")

    description = complaint_dict["description"].strip()
    if not description:
        raise ValueError("Description cannot be empty")

    description_lower = description.lower()

    # Check for severity keywords (case-insensitive search)
    has_severity_keyword = any(
        keyword in description_lower for keyword in SEVERITY_KEYWORDS
    )

    # Classify category and detect ambiguity
    category, is_ambiguous = _classify_category(description_lower)

    # Enforcement: Category must be from allowed list
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"Classified category '{category}' not in allowed list")

    # Enforcement: If severity keywords present, priority MUST be Urgent
    if has_severity_keyword:
        priority = "Urgent"
    else:
        # Classify priority based on description
        priority = _classify_priority(description_lower)

    # Enforcement: Priority must be from allowed list
    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"Invalid priority: {priority}")

    # Generate reason that cites specific words from description
    reason = _generate_reason(description, category)

    # Enforcement: Reason must be exactly one sentence
    sentences = [s.strip() for s in reason.split('.') if s.strip()]
    if len(sentences) != 1:
        raise ValueError(f"Reason must be exactly one sentence, got {len(sentences)}")

    # Enforcement: Flag must be NEEDS_REVIEW if genuinely ambiguous, else blank
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    # Enforcement: Flag must be either NEEDS_REVIEW or blank
    if flag not in {"NEEDS_REVIEW", ""}:
        raise ValueError(f"Invalid flag value: {flag}")

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description_lower: str) -> Tuple[str, bool]:
    """
    Classifies complaint description into an exact category.
    Detects ambiguity when multiple categories match or when description is unclear.

    Returns:
        Tuple of (category_string, is_ambiguous_bool)
    """
    # Rule-based keyword matching for each category
    category_keywords = {
        "Pothole": ["pothole", "pit", "hole in", "crater"],
        "Flooding": ["flood", "waterlog", "stagnant water", "inundated"],
        "Streetlight": ["streetlight", "street light", "lamppost", "lamp", "lighting"],
        "Waste": ["waste", "garbage", "litter", "trash", "refuse", "dumping"],
        "Noise": ["noise", "loud", "sound", "horn", "shouting", "barking"],
        "Road Damage": ["road damage", "crack", "asphalt", "pavement", "broken road"],
        "Heritage Damage": ["heritage", "monument", "historic", "structure"],
        "Heat Hazard": ["heat", "hot", "temperature", "heat wave", "scorching"],
        "Drain Blockage": ["drain", "blockage", "clogged", "blocked", "sewage"],
    }

    # Match keywords and count matches per category
    matches = {}
    for category, keywords in category_keywords.items():
        count = sum(1 for kw in keywords if kw in description_lower)
        if count > 0:
            matches[category] = count

    # Determine category and ambiguity
    if len(matches) == 0:
        # No keyword match - classify as Other and flag as ambiguous
        return "Other", True
    elif len(matches) == 1:
        # Single category match - not ambiguous
        category = list(matches.keys())[0]
        return category, False
    else:
        # Multiple matches - genuinely ambiguous
        # Choose the category with most keyword matches
        category = max(matches, key=matches.get)
        return category, True


def _classify_priority(description_lower: str) -> str:
    """
    Classifies priority for complaints without severity keywords.
    """
    # Default to Standard priority
    # Can be enhanced with additional heuristics
    return "Standard"


def _generate_reason(description: str, category: str) -> str:
    """
    Generates a one-sentence reason that cites specific words from the description.

    Enforcement: Reason must cite specific words from complaint text
    """
    # Remove any existing periods and extra whitespace from description
    clean_desc = description.replace('.', ' ').replace('  ', ' ').strip()
    
    # Extract key information from description
    words = clean_desc.split()

    # Build reason with direct reference to complaint content
    if len(clean_desc) > 100:
        # Long description - summarize with key phrase (limit to first 15 words)
        snippet = " ".join(words[:15])
        reason = f"Classified as {category}: {snippet}"
    else:
        # Short description - include full text
        reason = f"Classified as {category}: {clean_desc}"

    # Ensure it's exactly one sentence ending with period
    reason = reason.rstrip('.')
    reason = reason + '.'

    return reason


def batch_classify(input_file: str, output_file: str) -> None:
    """
    Skill: batch_classify
    Reads input CSV, applies classify_complaint to each row, writes output CSV.

    Args:
        input_file: Path to input CSV with 'description' column
        output_file: Path to output CSV for results

    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If input is invalid or output violates enforcement rules
    """
    # Read input CSV
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                raise ValueError("Input CSV must contain 'description' column")
            rows = list(reader)
    except csv.Error as e:
        raise ValueError(f"Failed to parse input CSV: {e}")
    except Exception as e:
        raise ValueError(f"Failed to read input CSV: {e}")

    if not rows:
        raise ValueError("Input CSV is empty")

    # Process each row
    results = []
    seen_descriptions = {}

    for i, row in enumerate(rows):
        try:
            result = classify_complaint({"description": row["description"]})
            results.append(result)

            # Track categories by description for variation detection
            desc_hash = row["description"][:50].lower()
            if desc_hash in seen_descriptions:
                if seen_descriptions[desc_hash] != result["category"]:
                    raise ValueError(
                        f"Row {i+1}: Category variation detected for similar complaint types. "
                        f"Must use consistent exact category names."
                    )
            seen_descriptions[desc_hash] = result["category"]

        except ValueError as e:
            raise ValueError(f"Row {i+1}: {e}")
        except Exception as e:
            raise ValueError(f"Row {i+1}: Unexpected error during classification: {e}")

    # Validation: All categories must be from allowed list
    for i, result in enumerate(results):
        if result["category"] not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Row {i+1}: Invalid category '{result['category']}' not in allowed list"
            )

    # Validation: All priorities must be from allowed list
    for i, result in enumerate(results):
        if result["priority"] not in ALLOWED_PRIORITIES:
            raise ValueError(
                f"Row {i+1}: Invalid priority '{result['priority']}' not in allowed list"
            )

    # Validation: All reason fields must be present and cite complaint words
    for i, (row, result) in enumerate(zip(rows, results)):
        if not result["reason"] or not result["reason"].strip():
            raise ValueError(f"Row {i+1}: Reason field is empty")

        # Check that reason cites specific words from description
        desc_words_lower = set(
            word.lower().strip('.,;:!?') for word in row["description"].split()
        )
        reason_words_lower = set(
            word.lower().strip('.,;:!?') for word in result["reason"].split()
        )

        # Require at least some overlap (excluding common words like 'classified', 'as', 'is')
        common_words = {'classified', 'as', 'is', 'a', 'the', 'and', 'or', 'of'}
        cited_words = (desc_words_lower & reason_words_lower) - common_words

        if not cited_words:
            raise ValueError(
                f"Row {i+1}: Reason does not cite specific words from complaint description"
            )

    # Validation: Flag field must be either NEEDS_REVIEW or blank
    for i, result in enumerate(results):
        if result["flag"] not in {"NEEDS_REVIEW", ""}:
            raise ValueError(
                f"Row {i+1}: Invalid flag value '{result['flag']}'. Must be 'NEEDS_REVIEW' or blank."
            )

    # Write output CSV
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        raise ValueError(f"Failed to write output CSV: {e}")


def main():
    """
    Main entry point. Accepts --input and --output arguments.
    """
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier: Classify citizen complaints with enforcement rules"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file with complaint descriptions"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file for classifications"
    )

    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"Success: Classified complaints written to {args.output}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
