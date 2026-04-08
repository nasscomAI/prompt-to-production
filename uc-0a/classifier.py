import argparse
import csv
import os
import sys

# Allowed taxonomy as defined in README.md and agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords that trigger 'Urgent' priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint description into its category, priority, reason, and flag.
    Strictly follows the enforcement rules in agents.md.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    # Rule: Refusal/Ambiguity condition
    if not description or len(description) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is either missing or too short to be accurately classified.",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()
    
    # Mapping of keywords to categories (Rule 1: Exact category strings)
    category_map = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "waterlogging", "submerged", "water accumulation"],
        "Streetlight": ["streetlight", "street light", "lamp", "darkness"],
        "Waste": ["garbage", "waste", "trash", "dumping", "rubbish"],
        "Noise": ["noise", "loud", "sound", "volume"],
        "Road Damage": ["road damage", "pavement", "crack", "uneven road"],
        "Heritage Damage": ["heritage", "monument", "historical", "statue"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "thermal"],
        "Drain Blockage": ["drain", "sewage", "gutter", "blockage", "clog"]
    }

    detected_category = "Other"
    category_trigger = ""

    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in text:
                detected_category = cat
                category_trigger = kw
                break
        if detected_category != "Other":
            break

    # Rule 2: Priority detection based on severity keywords
    priority = "Standard"
    severity_trigger = ""
    for kw in SEVERITY_KEYWORDS:
        if kw in text:
            priority = "Urgent"
            severity_trigger = kw
            break

    # Rule 3: Single sentence reason citing specific words
    if detected_category != "Other":
        cite_words = f"'{category_trigger}'"
        if severity_trigger:
            cite_words += f" and '{severity_trigger}'"
        reason = f"Classification is based on the mention of {cite_words} in the description."
    else:
        if severity_trigger:
            reason = f"Category is 'Other' but flagged as Urgent due to the word '{severity_trigger}'."
        else:
            reason = "No predefined category keywords were identified in the provided description."

    # Rule 4: Ambiguity flag
    flag = ""
    if detected_category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": detected_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV, classifies each complaint, and writes the results.
    Includes fatal error handling for missing files as specified in skills.md.
    """
    if not os.path.exists(input_path):
        print(f"FATAL ERROR: Input file not found at {input_path}")
        sys.exit(1)

    results = []

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames or "description" not in reader.fieldnames:
                print(f"FATAL ERROR: Input CSV at {input_path} is missing the required 'description' column.")
                sys.exit(1)

            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as e:
                    # Individual row failure - flag for review instead of stopping
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

    except Exception as e:
        print(f"FATAL ERROR: An unexpected error occurred while reading the input file: {e}")
        sys.exit(1)

    # Write output CSV
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} rows. Results saved to {output_path}")
    except Exception as e:
        print(f"FATAL ERROR: Could not write output to {output_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)