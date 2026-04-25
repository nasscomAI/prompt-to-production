"""
UC-0A — Complaint Classifier
Implements classification guided by agents.md enforcement rules and skills.md specifications.
"""
import argparse
import csv
import os
from pathlib import Path

# Allowed categories from classification schema
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category detection keywords (lowercase for case-insensitive matching)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pit", "crater", "hole in road"],
    "Flooding": ["flooded", "flood", "water", "submerged", "knee-deep", "overflowing", "waterlogged"],
    "Streetlight": ["streetlight", "street light", "light", "dark", "lighting", "flickering", "sparking", "electrical hazard"],
    "Waste": ["garbage", "waste", "trash", "litter", "refuse", "bins", "dump"],
    "Noise": ["noise", "music", "sound", "loud", "noisy", "honking", "sound pollution"],
    "Road Damage": ["cracked", "sinking", "damaged", "surface", "pothole", "deteriorated"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "temple", "mosque", "church"],
    "Heat Hazard": ["heat", "temperature", "scorching", "burning", "heatwave"],
    "Drain Blockage": ["drain", "blocked", "clogged", "sewage"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input: dict with fields including 'complaint_id' and 'description'
    Output: dict with keys: category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle empty or unintelligible descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Insufficient description to classify",
            "flag": "NEEDS_REVIEW"
        }

    description_lower = description.lower()

    # Detect category by keyword matching
    category = detect_category(description_lower)

    # Determine priority based on severity keywords
    priority = "Urgent" if any(kw in description_lower for kw in SEVERITY_KEYWORDS) else "Standard"

    # Generate reason citing specific words from description
    reason = generate_reason(description, category, description_lower)

    # Set flag if genuinely ambiguous (multiple strong category matches)
    flag = "NEEDS_REVIEW" if is_ambiguous(description_lower, category) else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def detect_category(description_lower: str) -> str:
    """
    Detect category by matching keywords. Returns first matching category or 'Other'.
    """
    match_scores = {}

    # Score each category based on keyword matches
    for category, keywords in CATEGORY_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw in description_lower)
        if match_count > 0:
            match_scores[category] = match_count

    # Return category with highest score, or Other if no matches
    if match_scores:
        return max(match_scores, key=match_scores.get)
    return "Other"


def generate_reason(description: str, category: str, description_lower: str) -> str:
    """
    Generate a one-sentence reason citing specific words from the description.
    """
    keywords = CATEGORY_KEYWORDS.get(category, [])

    # Find the first keyword match in the description
    cited_word = None
    for kw in keywords:
        if kw in description_lower:
            # Extract the actual word from description (preserving case)
            kw_index = description_lower.find(kw)
            if kw_index != -1:
                cited_word = description[kw_index:kw_index + len(kw)]
            break

    if cited_word:
        return f"Classified as {category} due to mention of '{cited_word}' in complaint."
    elif category == "Other":
        return "Complaint does not match standard categories; requires manual review."
    else:
        return f"Classified as {category} based on complaint content."


def is_ambiguous(description_lower: str, primary_category: str) -> bool:
    """
    Determine if categorization is genuinely ambiguous.
    Returns True if multiple categories have strong matches or if primary category is 'Other'.
    """
    if primary_category == "Other":
        return True

    match_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw in description_lower)
        if match_count > 0:
            match_scores[category] = match_count

    # Ambiguous if 2+ categories have equal high match counts
    if len(match_scores) >= 2:
        sorted_scores = sorted(match_scores.values(), reverse=True)
        if sorted_scores[0] == sorted_scores[1]:
            return True

    return False


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles errors gracefully, flags nulls, produces output even if some rows fail.
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Read input CSV
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Error reading input file {input_path}: {e}")

    # Classify each row
    results = []
    for row_num, row in enumerate(rows, start=2):  # Start at 2 (after header)
        try:
            if "description" not in row:
                print(f"Warning: Row {row_num} missing 'description' field. Skipping.")
                continue

            classified = classify_complaint(row)
            # Include all original columns plus classification results
            output_row = {**row, **classified}
            results.append(output_row)
        except Exception as e:
            print(f"Warning: Error classifying row {row_num}: {e}. Skipping.")
            continue

    # Write output CSV
    if not results:
        print(f"Warning: No rows classified. Output file will be empty.")

    # Get all fieldnames (original + classification fields)
    fieldnames = list(rows[0].keys()) + ["category", "priority", "reason", "flag"] if rows else ["category", "priority", "reason", "flag"]
    # Remove duplicates and preserve order
    seen = set()
    fieldnames = [f for f in fieldnames if not (f in seen or seen.add(f))]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
