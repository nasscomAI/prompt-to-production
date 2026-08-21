import csv
import argparse
import re
SEVERITY_WORDS = [
    "injury", "child", "school", "hospital", "hospitalised", "hospitalized",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flooded", "floods", "flooding", "rainwater", "waterlogging", "underpass"],
    "Streetlight": ["streetlight", "street light", "light not working", "dark"],
    "Waste": ["garbage", "waste", "trash", "overflow", "not cleared"],
    "Noise": ["noise", "loudspeaker", "horn", "drilling", "engines"],
    "Road Damage": ["road collapsed", "collapsed", "crater", "broken road", "road damage", "damaged road"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "heatwave"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drainage", "drain", "blocked"]
}

def contains_word(text, keyword):
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None

def classify_complaint(text):
    text_lower = text.lower()
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matches.append((category, keyword))
                break

    severity_match = ""
    for word in SEVERITY_WORDS:
        if contains_word(text_lower, word):
            severity_match = word
            break

    if not matches:
        category = "Other"
        matched_word = "no clear category keyword"
        flag = "NEEDS_REVIEW"
    else:
        category, matched_word = matches[0]
        flag = ""

        # Only flag if the complaint is truly confusing, not just because drain + flooding appear together
        unique_categories = list(dict.fromkeys([m[0] for m in matches]))
        if len(unique_categories) > 1:
            if not (set(unique_categories) <= {"Flooding", "Drain Blockage"}):
                flag = "NEEDS_REVIEW"

    priority = "Urgent" if severity_match else "Standard"

    reason = f"Classified as {category} because the complaint mentions '{matched_word}'."
    if severity_match:
        reason += f" Marked Urgent because it mentions '{severity_match}'."

    return category, priority, reason, flag

def main(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = []

        for row in reader:
            description = row.get("description", "")
            category, priority, reason, flag = classify_complaint(description)

            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag
            rows.append(row)

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.input, args.output)