import csv
import argparse
import os
import re

# Allowed schema values
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword mapping for categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging"],
    "Streetlight": ["streetlight", "light not working", "lamp"],
    "Waste": ["garbage", "waste", "trash"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road damage", "crack", "broken road"],
    "Heritage Damage": ["heritage", "monument damage"],
    "Heat Hazard": ["heat", "hot", "sun exposure"],
    "Drain Blockage": ["drain", "sewage", "blocked drain"]
}


def normalize(text):
    return text.lower() if isinstance(text, str) else ""


def detect_category(text):
    text_lower = normalize(text)

    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matches.append(category)
                break

    # Ambiguity handling
    if len(matches) > 1:
        return "Other", True  # NEEDS_REVIEW
    elif len(matches) == 1:
        return matches[0], False
    else:
        return "Other", True


def detect_priority(text):
    text_lower = normalize(text)

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text_lower:
            return "Urgent"

    # default fallback
    return "Standard"


def generate_reason(text):
    text = text if isinstance(text, str) else ""

    # extract key phrase (first ~12 words)
    words = text.strip().split()
    snippet = " ".join(words[:12]) if words else "missing description"

    # enforce one sentence
    return f"Based on complaint text '{snippet}'."


def classify_complaint(row):
    try:
        description = None

        # Try likely column names
        for key in row:
            if key.lower() in ["description", "complaint", "text"]:
                description = row[key]
                break

        if not description or not str(description).strip():
            return {
                "category": "Other",
                "priority": "Low",
                "reason": "Based on complaint text 'missing description'.",
                "flag": "NEEDS_REVIEW"
            }

        category, ambiguous = detect_category(description)
        priority = detect_priority(description)

        reason = generate_reason(description)

        flag = "NEEDS_REVIEW" if ambiguous else ""

        # enforce allowed values strictly
        if category not in CATEGORIES:
            category = "Other"
            flag = "NEEDS_REVIEW"

        if priority not in PRIORITIES:
            priority = "Standard"

        # enforce reason non-empty
        if not reason:
            reason = "Based on complaint text 'missing description'."
            flag = "NEEDS_REVIEW"

        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    except Exception:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Based on complaint text 'missing description'.",
            "flag": "NEEDS_REVIEW"
        }


def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        raise Exception("Error: Invalid input file path")

    results = []

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            if not reader.fieldnames:
                raise Exception("Error: Invalid CSV format")

            for row in reader:
                result = classify_complaint(row)
                results.append(result)

    except Exception as e:
        raise Exception(f"Error processing input file: {str(e)}")

    # Ensure all rows processed
    if not results:
        raise Exception("Error: No rows processed")

    # Write output
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()
            for r in results:
                writer.writerow(r)

    except Exception:
        raise Exception("Error: Failed to write output file")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"✅ Classification completed. Output saved to {args.output}")
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()