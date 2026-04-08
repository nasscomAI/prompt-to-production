import argparse
import csv
import logging
import sys

# Setup basic logging for batch classification errors
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get("description", "") or "").lower()
    complaint_id = row.get("complaint_id", row.get("id", ""))

    # Strict categories based on agents.md
    categories = {
        "Pothole": ["pothole", "crater", "hole"],
        "Flooding": ["flood", "waterlogged", "submerge", "standing water"],
        "Streetlight": ["streetlight", "street light", "dark", "broken light", "no light"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "bin"],
        "Noise": ["noise", "loud", "music", "party", "sound", "volume"],
        "Road Damage": ["road", "pavement", "crack", "damage", "surface"],
        "Heritage Damage": ["heritage", "monument", "statue", "historic"],
        "Heat Hazard": ["heat", "sun", "hot", "dehydrat"],
        "Drain Blockage": ["drain", "block", "sewage", "clog", "overflow"]
    }

    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    # Evaluate Priority
    matched_urgent_words = [kw for kw in urgent_keywords if kw in description]
    if matched_urgent_words:
        priority = "Urgent"
        urgent_reason_word = matched_urgent_words[0]
    else:
        priority = "Standard"

    # Evaluate Category
    matched_categories = {}
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories[cat] = kw
                break

    flag = ""
    assigned_category = "Other"

    if len(matched_categories) == 1:
        assigned_category = list(matched_categories.keys())[0]
        category_reason = f"mentions '{matched_categories[assigned_category]}'"
    elif len(matched_categories) > 1:
        # Genuinely ambiguous or multiple categories
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
        category_reason = "contains conflicting category keywords"
    else:
        # No matches found
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
        category_reason = "contains no clearly identifiable category keywords"

    # Evaluate Reason
    if priority == "Urgent":
        reason = f"Priority is Urgent because it mentions '{urgent_reason_word}', and category is {assigned_category} as it {category_reason}."
    else:
        reason = f"Category is {assigned_category} as the description {category_reason}."

    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, start=1):
                try:
                    if not row or not any(row.values()):
                        logging.warning(f"Row {row_num} is empty or null, skipping.")
                        continue
                    
                    classified_row = classify_complaint(row)
                    
                    # Ensure all required fields are present
                    out_row = {
                        "complaint_id": classified_row.get("complaint_id", row.get("complaint_id", row.get("id", ""))),
                        "category": classified_row.get("category", "Other"),
                        "priority": classified_row.get("priority", "Standard"),
                        "reason": classified_row.get("reason", ""),
                        "flag": classified_row.get("flag", "")
                    }
                    results.append(out_row)
                except Exception as e:
                    logging.error(f"Error processing row {row_num}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", row.get("id", f"error_row_{row_num}")),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        sys.exit(1)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        logging.error(f"Failed to write to output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
