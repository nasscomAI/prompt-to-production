import argparse
import csv
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", 
    "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORIES_MAP = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "floods", "flooded", "water", "rain"],
    "Streetlight": ["streetlight", "lights out", "light", "dark"],
    "Waste": ["waste", "garbage", "trash", "dead animal", "smell", "dumped"],
    "Noise": ["noise", "music", "loud", "sound"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "broken", "cave-in", "tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "temperature", "sun"],
    "Drain Blockage": ["drain", "manhole", "sewer", "clog"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to skills.md and agents.md.
    Returns: dict with exactly four keys: category, priority, reason, flag
    """
    desc = row.get("description", "").strip()

    # Error handling: empty_or_missing_description
    if not desc:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "The description was absent or unreadable.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()
    matched_categories = []
    matched_phrases = []

    # Map categories by matching exact substrings to rules
    for cat, kws in CATEGORIES_MAP.items():
        for kw in kws:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_phrases.append(kw)
                break

    # Flag: NEEDS_REVIEW when ambiguous (matching multiple different categories)
    flag = ""
    if len(matched_categories) > 1:
        flag = "NEEDS_REVIEW"
        category = matched_categories[0]  # Closest match
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        category = "Other"

    # Taxonomy drift & category_not_in_allowed_list validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    # Priority mapping enforcing severity keywords
    priority = "Standard"
    sev_match = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            sev_match = kw
            break

    # Extract reason exactly as one sentence citing the specific words
    if matched_phrases:
        cites = '", "'.join(matched_phrases)
        if sev_match and sev_match not in matched_phrases:
            reason = f'The description mentions "{cites}" and "{sev_match}".'
        else:
            reason = f'The description mentions "{cites}".'
    else:
        if sev_match:
            reason = f'The description mentions "{sev_match}".'
        else:
            snippet = " ".join(desc.split()[:5])
            reason = f'The description states "{snippet}".'

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads a city complaint CSV file, applies classify_complaint independently 
    to each row, and writes a results CSV containing the four classification fields.
    """
    # Error handling: input_file_not_found
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing file path: {input_path}")

    results = []
    input_row_count = 0

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for index, row in enumerate(reader):
                input_row_count += 1
                try:
                    # Apply classification independently
                    classification = classify_complaint(dict(row))
                except Exception as e:
                    # Error handling: classify_complaint_failure_on_a_row
                    print(f"Error processing row {index}: {e}")
                    classification = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error during classification.",
                        "flag": "NEEDS_REVIEW"
                    }
                results.append(classification)
    except Exception as e:
        raise RuntimeError(f"Failed to read input CSV: {e}")

    # Error handling: row_count_mismatch
    if len(results) != input_row_count:
        raise ValueError("Output row count does not equal input row count.")

    # Error handling: output_write_failure
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        raise IOError(f"Descriptive error writing to target path {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input test CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified records formatted into 4 columns and written to {args.output}")