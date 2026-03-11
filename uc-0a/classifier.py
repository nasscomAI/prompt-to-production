import csv
import argparse

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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def detect_priority(text):
    lower = text.lower()
    for word in SEVERITY_KEYWORDS:
        if word in lower:
            return "Urgent", word
    return "Standard", None


def detect_category(text):
    lower = text.lower()

    if "pothole" in lower:
        return "Pothole", "pothole"
    if "flood" in lower or "waterlogging" in lower:
        return "Flooding", "flood"
    if "streetlight" in lower or "dark street" in lower:
        return "Streetlight", "streetlight"
    if "garbage" in lower or "trash" in lower or "waste" in lower:
        return "Waste", "garbage"
    if "noise" in lower or "loud" in lower:
        return "Noise", "noise"
    if "road cracked" in lower or "road damage" in lower:
        return "Road Damage", "road"
    if "heritage" in lower or "monument" in lower:
        return "Heritage Damage", "heritage"
    if "heat" in lower:
        return "Heat Hazard", "heat"
    if "drain" in lower or "sewer" in lower:
        return "Drain Blockage", "drain"

    return "Other", None


def classify_complaint(text):

    category, keyword = detect_category(text)

    priority, severity_word = detect_priority(text)

    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"

    if severity_word:
        reason = f"Urgent because complaint mentions '{severity_word}'."
    elif keyword:
        reason = f"Classified as {category} because complaint mentions '{keyword}'."
    else:
        reason = "No clear category keywords found."

    if priority == "Standard" and category == "Other":
        priority = "Low"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:

        text = row.get("description") or row.get("complaint") or ""

        category, priority, reason, flag = classify_complaint(text)

        row["category"] = category
        row["priority"] = priority
        row["reason"] = reason
        row["flag"] = flag

    fieldnames = rows[0].keys()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print("Classification complete.")


if __name__ == "__main__":
    main()