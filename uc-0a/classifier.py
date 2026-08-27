import csv
import argparse
import sys
import os

# Allowed schema values as defined in agents.md
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword mapping to assign categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole in road", "crater"],
    "Flooding": ["flood", "waterlogging", "water logging", "water", "inundat"],
    "Streetlight": ["streetlight", "street light", "lamp", "dark street", "no light", "pole"],
    "Waste": ["waste", "garbage", "trash", "dump", "rubbish"],
    "Noise": ["noise", "loud", "sound", "music"],
    "Road Damage": ["road damage", "broken road", "cracked", "cave in", "road"],
    "Heritage Damage": ["heritage", "monument", "historical", "statue"],
    "Heat Hazard": ["heat", "hot", "sun", "temperature"],
    "Drain Blockage": ["drain", "blocked", "sewage", "clogged", "sewer", "overflow"]
}

def classify_complaint(text):
    """
    Skill 1: classify_complaint
    Classifies a single civic complaint into category, priority, reason, and flag
    based strictly on the predefined schema and rules.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Empty or invalid complaint string.")

    text_lower = text.lower()
    matched_categories: list[str] = []
    cited_category_words: list[str] = []

    # Detect category matches
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched_categories.append(cat)
                cited_category_words.append(kw)
                break

    # Determine category and ambiguity flag
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = matched_categories[0]  # Closest valid fallback: pick first deterministic
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority detection
    priority = "Standard"
    cited_severity_words: list[str] = []
    for kw in SEVERITY_KEYWORDS:
        if kw in text_lower:
            priority = "Urgent"
            cited_severity_words.append(kw)

    # Build reliable one-sentence reason citing specific words
    citation_phrases = cited_category_words + cited_severity_words
    
    if citation_phrases:
        limit = min(len(citation_phrases), 3)
        citations = ", ".join(f"'{citation_phrases[i]}'" for i in range(limit))
        reason = f"Classified as {category} with {priority} priority because the text explicitly mentions {citations}."
    else:
        # Fallback citation to maintain justification
        snippet = text.strip()[:40].replace('\n', ' ')
        reason = f"Classified as Other due to lack of distinct keywords, citing text snippet '{snippet}...'."

    # Enforce allowed schema (Error handling: refuse invalid output)
    if category not in CATEGORIES:
        raise ValueError(f"Category '{category}' is outside the allowed list.")
    if priority not in PRIORITIES:
        raise ValueError(f"Priority '{priority}' is outside the allowed list.")
    if flag not in ["", "NEEDS_REVIEW"]:
        raise ValueError(f"Invalid flag '{flag}'.")
    if not reason.endswith("."):
        reason += "."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):
    """
    Skill 2: batch_classify
    Processes an input CSV file of complaints, applies classify_complaint to each row,
    and writes a structured output CSV file.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file missing or unreadable: {input_path}")
        sys.exit(1)

    results = []
    input_row_count = 0

    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                raise ValueError("CSV is empty or improperly formatted.")

            # Identify the complaint text column (often 'description', 'complaint', or just the last/only available text column)
            text_column = None
            for col in ["description", "complaint", "text"]:
                if col in fieldnames:
                    text_column = col
                    break
            if not text_column:
                # Fallback to the first column
                text_column = fieldnames[0]

            for row in reader:
                input_row_count += 1
                complaint_text = str(row.get(text_column, ""))

                try:
                    result = classify_complaint(complaint_text)
                except ValueError as ve:
                    # Skip classification but fulfill row count and schema requirements
                    print(f"Error processing row {input_row_count}: {ve}")
                    result = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Classified as Other because input data was invalid or missing.",
                        "flag": "NEEDS_REVIEW"
                    }
                
                results.append(result)
                
    except Exception as e:
        print(f"Critical error processing batch: {e}")
        sys.exit(1)

    # Ensure output row count matches input row count
    if len(results) != input_row_count:
        print("Error: Output row count does not match input row count.")
        sys.exit(1)

    # Output to CSV
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Deterministic Complaint Classifier Agent")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
