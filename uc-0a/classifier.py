import csv
import argparse

# Allowed categories
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
    "Other"
]

# Category keyword mapping
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging", "water log", "flooding"],
    "Streetlight": ["streetlight", "street light", "light not working", "lamp"],
    "Waste": ["garbage", "waste", "trash", "dump"],
    "Noise": ["noise", "loud", "sound", "horn"],
    "Road Damage": ["road damage", "road crack", "broken road"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "hot surface"],
    "Drain Blockage": ["drain", "sewer", "drainage"]
}

# Severity keywords for urgent priority
SEVERITY_KEYWORDS = [
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


def classify_complaint(description):
    text = description.lower()

    category = None
    matched_keyword = None

    # Determine category
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in text:
                category = cat
                matched_keyword = word
                break
        if category:
            break

    # If no category matched
    flag = ""
    if not category:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Determine priority
    priority = "Standard"
    severity_word = None

    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"
            severity_word = word
            break

    # Generate reason
    if matched_keyword and severity_word:
        reason = f'Contains words "{matched_keyword}" and "{severity_word}"'
    elif matched_keyword:
        reason = f'Contains word "{matched_keyword}"'
    elif severity_word:
        reason = f'Contains severity word "{severity_word}"'
    else:
        reason = "No clear category keyword found"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        rows = []

        for row in reader:
            description = row.get("description", "")
            category, priority, reason, flag = classify_complaint(description)

            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag

            rows.append(row)

    with open(output_file, "w", newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
