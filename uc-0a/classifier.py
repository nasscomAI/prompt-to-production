"""
UC-0A — Complaint Classifier
Built from agents.md and skills.md
"""
import argparse
import csv
import sys

# Priority keywords mapping exactly to the rules in agents.md
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Category keywords mapping ensuring no hallucinated sub-categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "waterlogging"],
    "Streetlight": ["streetlight", "lights out", "dark", "sparking"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dump", "animal"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["crack", "road surface", "broken", "cave-in", "manhole", "footpath", "tyre damage"],
    "Heritage Damage": ["heritage", "monument", "statue", "historical"],
    "Heat Hazard": ["heatwave", "heat hazard", "temperature", "sunstroke"],
    "Drain Blockage": ["drain", "clogged", "sewage", "block"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint to determine category, priority, reason, and flag.
    Returns: dict with all original fields + new classification fields.
    """
    description = row.get("description", "").lower()
    
    # Priority
    priority = "Standard"
    urgent_word_found = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            urgent_word_found = kw
            break
            
    # Category
    matched_categories = []
    matched_words = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                matched_categories.append(cat)
                matched_words.append(kw)
                break
                
    # Evaluate flags and construct one-sentence reason
    category = "Other"
    flag = ""
    reason = "The complaint is classified based on its description."
    
    if len(description.strip()) == 0:
        priority = "Low"
        flag = "NEEDS_REVIEW"
        reason = "The description is empty and could not be evaluated."
    elif len(matched_categories) == 0:
        flag = "NEEDS_REVIEW"
        reason = "The description did not contain clear keywords matching predefined categories."
    elif len(matched_categories) > 1:
        flag = "NEEDS_REVIEW"
        reason = f"The category is ambiguous due to multiple matches, such as '{matched_words[0]}' and '{matched_words[1]}'."
    else:
        category = matched_categories[0]
        word = matched_words[0]
        if urgent_word_found:
            reason = f"Classified as {category} because it mentions '{word}', and prioritized Urgent due to the word '{urgent_word_found}'."
        else:
            reason = f"Classified as {category} because the description explicitly cites '{word}'."

    # Return new dict to avoid modifying original row in place unintentionally
    result = dict(row)
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row safely, and write the output.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            rows = list(reader)
            if not rows:
                print(f"Warning: File {input_path} is empty or has no rows.", file=sys.stderr)
                return
            
            # Add our new fields
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            # Only add them if not already present
            for field in ["category", "priority", "reason", "flag"]:
                if field not in fieldnames:
                    fieldnames.append(field)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as fout:
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()
                for i, row in enumerate(rows):
                    try:
                        out_row = classify_complaint(row)
                        writer.writerow(out_row)
                    except Exception as e:
                        print(f"Error processing row {i}: {e}. Skipping.", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
