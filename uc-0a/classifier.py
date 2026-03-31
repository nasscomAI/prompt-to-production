import csv
import argparse

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(text):
    text_lower = text.lower()

    # -------- CATEGORY --------
    if "pothole" in text_lower:
        category = "Pothole"
    #elif "flood" in text_lower or "waterlogging" in text_lower:
    elif "flood" in text_lower or "waterlogging" in text_lower or "water" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower:
        category = "Noise"
    #elif "road" in text_lower:
    elif "road" in text_lower or "crack" in text_lower or "damage" in text_lower:
        category = "Road Damage"
    elif "heritage" in text_lower:
        category = "Heritage Damage"
    elif "heat" in text_lower:
        category = "Heat Hazard"
    elif "drain" in text_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    # -------- PRIORITY --------
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text_lower:
            priority = "Urgent"
            break

    # -------- REASON --------
    #reason = f"Detected keywords in description: '{text[:50]}'"

    found_severity = [w for w in SEVERITY_KEYWORDS if w in text_lower]

    category_keywords = []
    if "pothole" in text_lower: category_keywords.append("pothole")
    if "flood" in text_lower or "waterlogging" in text_lower: category_keywords.append("flood")
    if "light" in text_lower: category_keywords.append("light")
    if "garbage" in text_lower or "waste" in text_lower: category_keywords.append("garbage")
    if "noise" in text_lower: category_keywords.append("noise")
    if "road" in text_lower: category_keywords.append("road")
    if "drain" in text_lower: category_keywords.append("drain")

    all_keywords = found_severity + category_keywords

    reason = f"Detected words: {', '.join(all_keywords) if all_keywords else text[:40]}"

    # -------- FLAG --------
    #flag = ""
    #if category == "Other":
    #    flag = "NEEDS_REVIEW"

    flag = ""

    if category == "Other" or len(text.split()) < 3:
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:
            text = row.get("description", "")
            category, priority, reason, flag = classify_complaint(text)

            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag

            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)