import argparse
import csv
import os
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging", "water logging"],
    "Streetlight": ["streetlight", "street light", "light not working", "no light"],
    "Waste": ["garbage", "waste", "trash", "bin"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["road damage", "broken road", "cracked road"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain", "sewer", "blockage", "clog"]
}


def contains_severity(text):
    text_lower = text.lower()
    return any(word in text_lower for word in SEVERITY_KEYWORDS)


def detect_category(text):
    text_lower = text.lower()
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matches.append(category)
                break

    matches = list(set(matches))

    if len(matches) == 1:
        return matches[0], False
    elif len(matches) == 0:
        return "Other", True
    else:
        return matches[0], True  # ambiguous


def generate_reason(text):
    words = text.strip().split()
    snippet = " ".join(words[:8]) if words else "missing description"
    reason = f'Based on "{snippet}" in the complaint.'
    if not reason.endswith("."):
        reason += "."
    return reason


def classify_complaint(row):
    description = ""

    if isinstance(row, dict):
        description = row.get("description", "") or row.get("complaint", "")
    else:
        description = str(row)

    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": 'Complaint has "missing description".',
            "flag": "NEEDS_REVIEW"
        }

    category, ambiguous = detect_category(description)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        ambiguous = True

    priority = "Standard"
    if contains_severity(description):
        priority = "Urgent"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    reason = generate_reason(description)

    if '"' not in reason:
        reason = f'Based on "{description[:15]}" in the complaint.'

    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    results = []

    try:
        with open(input_path, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                print("Error: Malformed CSV file.")
                sys.exit(1)

            for row in reader:
                result = classify_complaint(row)

                # Enforcement corrections
                if contains_severity(str(row)):
                    result["priority"] = "Urgent"

                if result["category"] not in ALLOWED_CATEGORIES:
                    result["category"] = "Other"
                    result["flag"] = "NEEDS_REVIEW"

                if not result.get("reason"):
                    result["reason"] = 'Based on "missing description" in the complaint.'

                if result["flag"] not in ["NEEDS_REVIEW", ""]:
                    result["flag"] = "NEEDS_REVIEW"

                results.append(result)

    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for r in results:
                for field in fieldnames:
                    if field not in r:
                        r[field] = ""

                writer.writerow({
                    "category": r["category"],
                    "priority": r["priority"],
                    "reason": r["reason"],
                    "flag": r["flag"]
                })

    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()