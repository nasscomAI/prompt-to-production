"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md constraints.
"""
import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # Determine priority based on severity keywords
    priority = "Standard"
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    if found_severity:
        priority = "Urgent"

    # Determine category deterministically
    found_categories = set()
    category_reasons = []

    def check(words, cat):
        for w in words:
            if w in description:
                found_categories.add(cat)
                category_reasons.append(w)

    check(['pothole'], "Pothole")
    check(['flood', 'water'], "Flooding")
    check(['light', 'dark'], "Streetlight")
    check(['waste', 'garbage', 'dead animal', 'dumped', 'trash'], "Waste")
    check(['music', 'noise', 'loud'], "Noise")
    check(['crack', 'broken', 'sinking', 'manhole'], "Road Damage")
    check(['heritage', 'monument'], "Heritage Damage")
    check(['heat'], "Heat Hazard")
    check(['drain', 'block'], "Drain Blockage")
    
    category = "Other"
    flag = ""
    reason = ""

    all_matched_words = list(set(category_reasons + found_severity))
    words_citation = ", ".join([f"'{w}'" for w in all_matched_words]) if all_matched_words else "no specific keywords"

    # Enforce classification rules and ambiguity flag
    if len(found_categories) == 1:
        category = list(found_categories)[0]
        reason = f"Classified as {category} with {priority} priority citing the words: {words_citation}."
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous description matched multiple categories citing the words: {words_citation}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Could not determine category from description; cited words: {words_citation}."

    return {
        "complaint_id": row.get('complaint_id', ''),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row_num, row in enumerate(reader, start=1):
                    cid = row.get("complaint_id", f"UNKNOWN_ID_{row_num}")
                    try:
                        # Handle null/missing descriptions
                        if not row.get("description"):
                            writer.writerow({
                                "complaint_id": cid,
                                "category": "Other",
                                "priority": "Standard",
                                "reason": "Empty or missing description prevents classification.",
                                "flag": "NEEDS_REVIEW"
                            })
                            continue
                            
                        classification = classify_complaint(row)
                        writer.writerow(classification)
                        
                    except Exception as e:
                        # Log and flag malformed rows without crashing
                        print(f"Error processing row {row_num}: {str(e)}")
                        writer.writerow({
                            "complaint_id": cid,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"System error during processing: {str(e)}",
                            "flag": "NEEDS_REVIEW"
                        })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Failed to process batch: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
