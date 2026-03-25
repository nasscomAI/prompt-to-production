import argparse
import csv
import sys

# Allowed exact categories from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords mapping to 'Urgent' priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Simple heuristic mapping for classification based strictly on string matching
KEYWORD_TO_CATEGORY = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "dark": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "animal": "Waste",
    "dump": "Waste",
    "noise": "Noise",
    "music": "Noise",
    "road": "Road Damage",
    "crack": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "manhole": "Drain Blockage"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based strictly on defined agents.md rules.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = str(row.get("description") or "").lower()
    
    # Check severity
    urgent_matches = [kw for kw in URGENT_KEYWORDS if kw in description]
    priority = "Urgent" if urgent_matches else "Standard"
    
    # Check category
    matched_categories = set()
    category_triggers = []
    
    for word, cat in KEYWORD_TO_CATEGORY.items():
        if word in description:
            matched_categories.add(cat)
            category_triggers.append(word)
            
    # Apply Refusal/Ambiguity condition
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        flag = ""
        trigger = category_triggers[0]
        
        reason_parts = [f"Classified as {category} because the description contains the word '{trigger}'"]
        if urgent_matches:
            reason_parts.append(f"and prioritized as Urgent due to the severity keyword '{urgent_matches[0]}'")
        reason = " ".join(reason_parts) + "."
    else:
        # 0 or >1 categories matched -> genuinely ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(matched_categories) > 1:
            reason = f"Category is ambiguous due to multiple conflicting keywords ({', '.join(category_triggers)})."
        else:
            reason = "Category cannot be determined from the description alone."
            
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV robustly.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("Input CSV is empty or missing headers.")
                
            # Add new fields for output
            output_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]
            
            with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fields)
                writer.writeheader()
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        classification = classify_complaint(row)
                        # Merge classification into the row
                        row.update(classification)
                        writer.writerow(row)
                    except Exception as e:
                        # Error handling matching skills.md: logs error, marks failed row, continues
                        print(f"Error processing row {row_num}: {e}")
                        row.update({
                            "category": "Other", 
                            "priority": "Low", 
                            "reason": f"Processing error: {str(e)}", 
                            "flag": "NEEDS_REVIEW"
                        })
                        writer.writerow(row)
                        
    except Exception as e:
        print(f"Failed to run batch_classify: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
