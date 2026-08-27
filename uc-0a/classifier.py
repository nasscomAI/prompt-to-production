"""
UC-0A — Complaint Classifier
Implements RICE → agents.md → skills.md workflow for citizen complaint classification.
"""
import argparse
import csv
import re

# Allowed categories (exact strings from classification schema)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category detection patterns (keywords + weights for disambiguation)
CATEGORY_PATTERNS = {
    "Pothole": r"\b(pothole|pit|crater|hole|bump|uneven|sunken|road surface)\b",
    "Flooding": r"\b(flood|water|waterlogging|drain|blocked drain|submerged|inundated)\b",
    "Streetlight": r"\b(light|streetlight|bulb|lamp|dark|not working|broken light|power)\b",
    "Waste": r"\b(garbage|waste|trash|litter|rubbish|debris|dump|waste dump)\b",
    "Noise": r"\b(noise|sound|loud|honk|horn|music|construction|disturb)\b",
    "Road Damage": r"\b(road|surface|asphalt|pavement|broken road|damaged road|crack)\b",
    "Heritage Damage": r"\b(heritage|monument|historical|structure|building|ancient|temple|mosque|church)\b",
    "Heat Hazard": r"\b(heat|temperature|sun|hot|summer|heatwave|extreme heat)\b",
    "Drain Blockage": r"\b(drain|sewer|blocked|clogged|overflow|stagnant)\b",
}


def detect_category(description: str) -> tuple:
    """
    Detect category from description.
    Returns: (category, matched_words, ambiguity_flag)
    """
    if not description or not description.strip():
        return "Other", [], True  # Null/empty → Other + ambiguous flag
    
    desc_lower = description.lower()
    matches = {}
    
    # Count keyword matches per category
    for category, pattern in CATEGORY_PATTERNS.items():
        matched_words = re.findall(pattern, desc_lower, re.IGNORECASE)
        if matched_words:
            matches[category] = matched_words
    
    if not matches:
        return "Other", [], False  # No matches → Other, not ambiguous
    
    if len(matches) == 1:
        category = list(matches.keys())[0]
        matched_words = matches[category]
        return category, matched_words, False
    
    # Multiple categories matched → ambiguous, return Other + flag
    return "Other", [], True


def detect_priority(description: str) -> str:
    """
    Detect priority based on severity keywords.
    Returns: "Urgent" if severity keywords present, else "Standard"
    """
    if not description or not description.strip():
        return "Standard"
    
    desc_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r"\b" + keyword + r"\b", desc_lower):
            return "Urgent"
    
    return "Standard"


def generate_reason(description: str, category: str, matched_words: list) -> str:
    """
    Generate one-sentence reason citing specific words from description.
    """
    if matched_words:
        # Use first matched word(s) in reason
        words_str = ", ".join(matched_words[:2])
        return f"Complaint describes {category.lower()} with mention of {words_str}."
    
    if category == "Other":
        return "Complaint does not clearly match any category."
    
    return f"Classified as {category}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input: dict with keys: complaint_id, description
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Enforces: exact category strings, severity keyword triggers, reason citations, ambiguity flagging.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")
    
    # Handle null/empty description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is null or empty.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Detect category (with ambiguity flag)
    category, matched_words, is_ambiguous = detect_category(description)
    
    # Detect priority
    priority = detect_priority(description)
    
    # Generate reason
    reason = generate_reason(description, category, matched_words)
    
    # Set flag for ambiguous cases
    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each complaint row, write results CSV.
    Error handling: flags nulls, skips malformed rows with warning, always writes output.
    """
    processed = 0
    flagged = 0
    skipped = 0
    
    results = []
    
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames or "complaint_id" not in reader.fieldnames or "description" not in reader.fieldnames:
                print(f"WARNING: Input CSV must have 'complaint_id' and 'description' columns.")
                return
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                try:
                    result = classify_complaint(row)
                    results.append(result)
                    processed += 1
                    
                    if result["flag"] == "NEEDS_REVIEW":
                        flagged += 1
                    
                except Exception as e:
                    print(f"WARNING: Skipping row {row_num}: {e}")
                    skipped += 1
                    continue
        
        # Write results to output CSV
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # Log summary
        print(f"Processing complete:")
        print(f"  Processed: {processed} rows")
        print(f"  Flagged for review: {flagged} rows")
        print(f"  Skipped (errors): {skipped} rows")
        print(f"  Output written: {output_path}")
    
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
    except Exception as e:
        print(f"ERROR: Failed to process file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[techm].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
