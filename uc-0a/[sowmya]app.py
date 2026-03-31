import argparse
import csv
import sys

# Severity keywords that must trigger Urgent priority
URGENT_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'
]

# Supported categorization mappings matching required rules
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "water", "inundate", "flooded"],
    "Streetlight": ["streetlight", "light", "dark", "sparking"],
    "Waste": ["waste", "garbage", "trash", "animal", "dump", "smell"],
    "Noise": ["noise", "loud", "music", "party"],
    "Road Damage": ["road", "crack", "sinking", "manhole", "footpath", "broken", "tiles"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "temperature", "wave"],
    "Drain Blockage": ["drain", "clog", "blockage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classifies one raw citizen complaint row into exact category, priority, reason, and flag fields.
    """
    if not isinstance(row, dict) or 'description' not in row:
        return {
            "category": "Other", 
            "priority": "Low", 
            "reason": "Missing or malformed description in the input record.", 
            "flag": "NEEDS_REVIEW"
        }

    desc = row.get("description", "").lower()
    category = "Other"
    priority = "Standard"
    reason = "Could not identify a distinct sub-category from the description."
    flag = "NEEDS_REVIEW"
    
    # Ensure priority is Urgent if severity keywords match
    found_urgent_words = [w for w in URGENT_KEYWORDS if w in desc]
    if found_urgent_words:
        priority = "Urgent"

    # Identify categories via exact rules
    matched_categories = []
    reason_words = []
    for cat, words in CATEGORY_KEYWORDS.items():
        matched = [w for w in words if w in desc]
        if matched:
            if cat not in matched_categories:
                matched_categories.append(cat)
                reason_words.append(matched[0])

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = f"Classified as {category} because description mentions '{reason_words[0]}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Classification ambiguous: matched multiple categories ({', '.join(matched_categories)})."

    if found_urgent_words:
        reason += f" The priority is Urgent due to the keyword '{found_urgent_words[0]}'."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Iterates through the input CSV file to apply classify_complaint to each row and writes the structured output CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("The provided input file has no headers.")
            
            output_fields = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fields)
                writer.writeheader()
                
                rows_processed = 0
                for row in reader:
                    try:
                        classification = classify_complaint(row)
                        for k, v in classification.items():
                            row[k] = v
                        writer.writerow(row)
                        rows_processed += 1
                    except Exception as loop_err:
                        row["category"] = "Other"
                        row["priority"] = "Low"
                        row["reason"] = f"Fatal record parsing fault: {str(loop_err)}"
                        row["flag"] = "NEEDS_REVIEW"
                        writer.writerow(row)
                        rows_processed += 1
                        
        print(f"Done. Processed {rows_processed} rows and wrote results to {output_path}.")
    except FileNotFoundError:
        print(f"FAILED: The input file {input_path} could not be found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"FAILED: An unexpected file handling error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to output results_[city].csv")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
