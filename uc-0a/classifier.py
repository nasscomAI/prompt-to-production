"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description text.
    Returns: dict with updated keys including category, priority, reason, flag.
    """
    description = row.get("description", "").lower()
    
    # Apply severity check for Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_severity = [kw for kw in severity_keywords if kw in description]
    
    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Maps category keywords based on the allowed category taxonomy
    category_map = {
        'Pothole': ['pothole'],
        'Drain Blockage': ['drain', 'manhole', 'sewer'],
        'Flooding': ['flood', 'waterlog'],
        'Streetlight': ['light', 'dark', 'lamp'],
        'Waste': ['waste', 'garbage', 'trash', 'dump', 'animal'],
        'Noise': ['noise', 'music', 'loud', 'sound'],
        'Road Damage': ['road surface', 'broken', 'crack', 'footpath'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heat', 'temperature']
    }
    
    found_cats = []
    matched_cat_keywords = []
    
    # Evaluate all categories to detect ambiguity
    for cat, keywords in category_map.items():
        found = [kw for kw in keywords if kw in description]
        if found:
            found_cats.append(cat)
            matched_cat_keywords.extend(found)
            
    # Apply ambiguity rule
    flags = ""
    if len(found_cats) == 1:
        category = found_cats[0]
    else:
        # Genuinely ambiguous (multiple categories or none)
        category = "Other"
        flags = "NEEDS_REVIEW"
        
    # Construct justification sentence stating exactly which words were referenced
    reason_words = list(set(matched_severity + matched_cat_keywords))
    if not reason_words:
        reason = "The description lacked clear matching keywords and could not be determined."
    else:
        reason = f"Classified because the description contained words like: {', '.join(reason_words)}."
    
    output_row = row.copy()
    output_row["category"] = category
    output_row["priority"] = priority
    output_row["reason"] = reason
    output_row["flags"] = flags  # Use 'flags' as requested by the user
    
    return output_row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Skips malformed rows and flags any ambiguous classifications.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    # Skip malformed/crashing row safely
                    continue
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    if not results:
        print("No valid rows were processed.")
        return
        
    out_fields = fieldnames + ["category", "priority", "reason", "flags"]
    # Ensure no duplicate fieldnames maintaining order
    seen = set()
    out_fields = [x for x in out_fields if not (x in seen or seen.add(x))]
    
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
