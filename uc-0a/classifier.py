"""
UC-0A — Complaint Classifier
Built according to agents.md and skills.md.
"""
import argparse
import csv
import re

# Categories per agents.md and README.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "floods"],
    "Streetlight": ["streetlight", "lights", "dark"],
    "Waste": ["garbage", "waste", "animal"],
    "Noise": ["noise", "music"],
    "Road Damage": ["crack", "sinking", "road surface", "broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain blocked", "drain", "manhole"]
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def get_sentence_with_word(text: str, word: str) -> str:
    """Extracts a sentence containing the specific word."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    for sentence in sentences:
        if word.lower() in sentence.lower():
            return sentence.strip()
    return text.strip()

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agent rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # 1. Determine Category
    matched_categories = []
    matched_cat_words = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_cat_words.append(kw)
                break
                
    if len(matched_categories) == 0:
        matched_category = "Other"
        matched_cat_word = ""
    elif len(matched_categories) == 1:
        matched_category = matched_categories[0]
        matched_cat_word = matched_cat_words[0]
    else:
        matched_category = "Other"
        matched_cat_word = ""

    # 2. Determine Priority
    priority = "Standard"
    matched_sev_word = ""
    for sev_kw in SEVERITY_KEYWORDS:
        if sev_kw in desc_lower:
            priority = "Urgent"
            matched_sev_word = sev_kw
            break

    # 3. Determine Flag
    if len(matched_categories) > 1 or len(matched_categories) == 0:
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # 4. Formulate Reason
    reason = ""
    if matched_sev_word:
        snippet = get_sentence_with_word(description, matched_sev_word)
        reason = f"The priority is Urgent because the description contains the severity keyword '{matched_sev_word}' ({snippet})."
    elif len(matched_categories) > 1:
        reason = f"The category is genuinely ambiguous because the description mentions multiple categories such as '{matched_cat_words[0]}' and '{matched_cat_words[1]}'."
    elif matched_cat_word:
        snippet = get_sentence_with_word(description, matched_cat_word)
        reason = f"The category is {matched_category} because the description mentions '{matched_cat_word}' ({snippet})."
    else:
        reason = "No specific category or severity keywords were found in the description."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    # Still produce output even if one row fails
                    results.append({
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error during processing: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Failed to read file '{input_path}': {e}")
        return

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output to '{output_path}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
