import argparse
import csv
import re

# --- CONSTANTS FROM agents.md ---
ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

PRIORITY_LEVELS = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

# --- KEYWORD MAPPING FOR CATEGORY ---
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole in road"],
    "Flooding": ["flood", "waterlogging", "water logged"],
    "Streetlight": ["streetlight", "light not working", "no light", "dark street"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["road broken", "road damage", "crack", "damaged road"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "hot", "temperature"],
    "Drain Blockage": ["drain", "blocked drain", "sewage", "clogged"],
}


def contains_severity(text):
    """Check if any severity keyword is present."""
    for word in SEVERITY_KEYWORDS:
        if re.search(rf"\b{word}\b", text):
            return word
    return None


def match_category(text):
    """Match text to one or more categories."""
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matches.append(category)
                break

    return matches


def classify_complaint(row):
    """Classify a single complaint row."""
    try:
        description = row.get("description", "")

        if not isinstance(description, str) or not description.strip():
            return {
                "category": "Other",
                "priority": "Low",
                "reason": "Invalid input: missing or malformed description",
                "flag": "NEEDS_REVIEW",
            }

        text = description.lower()

        # --- CATEGORY MATCHING ---
        matched_categories = match_category(text)

        if len(matched_categories) == 1:
            category = matched_categories[0]
            flag = ""
        elif len(matched_categories) > 1:
            # Ambiguous
            return {
                "category": "Other",
                "priority": "Standard",
                "reason": "Ambiguous complaint with overlapping keywords",
                "flag": "NEEDS_REVIEW",
            }
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"

        # --- PRIORITY DETECTION ---
        severity_word = contains_severity(text)

        if severity_word:
            priority = "Urgent"
        else:
            # Basic heuristic
            if category == "Other":
                priority = "Low"
            else:
                priority = "Standard"

        # --- REASON GENERATION ---
        if severity_word:
            reason = f"Detected keyword '{severity_word}' indicating urgency in description"
        elif matched_categories:
            reason = f"Matched keywords for category '{category}' in description"
        else:
            reason = "No clear category keywords found in description"

        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    except Exception:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Processing error occurred",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path, output_path):
    """Process CSV and classify all rows."""
    with open(input_path, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        rows = []

        for row in reader:
            try:
                if "description" not in row or not row["description"].strip():
                    result = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description field",
                        "flag": "NEEDS_REVIEW",
                    }
                else:
                    result = classify_complaint(row)

                row.update(result)
                rows.append(row)

            except Exception:
                row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Processing error occurred",
                    "flag": "NEEDS_REVIEW",
                })
                rows.append(row)

    # Write output
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
