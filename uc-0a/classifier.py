import argparse
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Valid categories defined by the RICE prompt
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", 
    "Noise", "Road Damage", "Heritage Damage", 
    "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords that trigger "Urgent" priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with original data plus category, priority, reason, flag.
    Driven by heuristics simulating the AI classification.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine priority based on enforcement rules
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            break
            
    # 2. Determine category and reason based on text matching
    category = "Other"
    flag = ""
    reason = "No specific category matched."
    
    if "pothole" in description:
        category = "Pothole"
        reason = "The description mentions a pothole affecting the road."
    elif "flood" in description or "water" in description and "drain" not in description:
        category = "Flooding"
        reason = "The description notes flooding or water logging."
    elif "drain" in description:
        category = "Drain Blockage"
        reason = "The description specifically points out a blocked drain."
    elif "light" in description or "dark" in description:
        category = "Streetlight"
        reason = "The description outlines an issue with streetlights or darkness."
    elif "garbage" in description or "waste" in description or "smell" in description or "animal" in description:
        category = "Waste"
        reason = "The description relates to garbage, bulk waste, or a dead animal."
    elif "music" in description or "noise" in description:
        category = "Noise"
        reason = "The description cites music or noise disturbance."
    elif "crack" in description or "surface" in description or "manhole" in description or "footpath" in description:
        category = "Road Damage"
        reason = "The description points to cracked surfaces or road damage."
    else:
        # Ambiguous case - flag for review as mandated by the rules
        flag = "NEEDS_REVIEW"
        category = "Other"
        reason = "The complaint lacked clear infrastructure keywords to assign a category."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle missing files, bad rows, and append classification fields.
    """
    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                # Append new classification columns
                fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
            else:
                logging.error("Input CSV is empty or missing headers.")
                return

            for row_num, row in enumerate(reader, start=1):
                try:
                    # Apply classification skill
                    classification = classify_complaint(row)
                    
                    # Merge results with original row data
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    logging.error(f"Error classifying row {row_num}: {e}")
                    # Handle individual row failure gracefully
                    row.update({
                        "category": "Error",
                        "priority": "Error",
                        "reason": f"Classification failed: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
                    results.append(row)
                    
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}")
        return
    except Exception as e:
        logging.error(f"Critical error reading input file: {e}")
        return

    # Write output to CSV
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            if not results:
                logging.warning("No valid results found. Empty file will be generated.")
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        logging.error(f"Failed to write results to output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified results written to {args.output}")
