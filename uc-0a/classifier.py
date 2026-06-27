import csv
import argparse

# Allowed categories (must match exactly)
CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
]

# Keyword mappings for categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole in road", "road hole"],
    "Flooding": ["flood", "waterlogging", "water logged", "overflow"],
    "Streetlight": ["streetlight", "light not working", "lamp", "dark street"],
    "Waste": ["garbage", "waste", "trash", "dump", "litter"],
    "Noise": ["noise", "loud", "sound", "disturbance"],
    "Road Damage": ["road damage", "crack", "broken road", "damaged road"],
    "Heritage Damage": ["heritage", "monument damage", "historic damage"],
    "Heat Hazard": ["heat", "high temperature", "burn", "hot surface"],
    "Drain Blockage": ["drain", "sewage", "blocked drain", "clogged"]
}

# Keywords that trigger Urgent priority
URGENT_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]


def clean_text(text):
    """Safely clean and normalize text."""
    if not text:
        return ""
    return str(text).lower().strip()


def find_category(description):
    """
    Returns:
    category, matched_words, ambiguous
    """
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                matches.append((category, keyword))

    found_categories = set(category for category, _ in matches)

    # No clear match
    if len(found_categories) == 0:
        return "Other", [], True

    # More than one category matched -> ambiguous
    if len(found_categories) > 1:
        words = [word for _, word in matches]
        return "Other", words, True

    # Exactly one category matched
    category = list(found_categories)[0]
    words = [word for _, word in matches]

    return category, words, False


def determine_priority(description):
    """Determine complaint priority."""
    matched_urgent_words = []

    for word in URGENT_KEYWORDS:
        if word in description:
            matched_urgent_words.append(word)

    if matched_urgent_words:
        return "Urgent", matched_urgent_words

    # Optional heuristic for Low priority
    if len(description.split()) <= 3:
        return "Low", []

    return "Standard", []


def process_file(input_file, output_file):
    """Read input CSV and write classified output CSV."""

    with open(input_file, "r", encoding="utf-8", newline="") as infile, \
         open(output_file, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = [
            "complaint_id",
            "category",
            "priority",
            "reason",
            "flag"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                complaint_id = row.get("complaint_id", "").strip()
                description = clean_text(row.get("description", ""))

                category, category_words, ambiguous = find_category(description)
                priority, priority_words = determine_priority(description)

                # Build reason using complaint words
                reasons = []

                if category_words:
                    reasons.append(
                        "category keywords: " +
                        ", ".join(category_words)
                    )

                if priority_words:
                    reasons.append(
                        "urgent keywords: " +
                        ", ".join(priority_words)
                    )

                if not reasons:
                    reasons.append("no clear keywords found")

                reason = "; ".join(reasons)

                flag = "NEEDS_REVIEW" if ambiguous else ""

                writer.writerow({
                    "complaint_id": complaint_id,
                    "category": category,
                    "priority": priority,
                    "reason": reason,
                    "flag": flag
                })

            except Exception as e:
                # Never crash; process all rows
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file"
    )

    args = parser.parse_args()

    process_file(args.input, args.output)

    print(f"Done. Results written to {args.output}")