import csv
import argparse

URGENT_KEYWORDS = ["injury", "child", "school", "hospital",
                   "ambulance", "fire", "hazard", "fell", "collapse"]

def classify(text):
    text_lower = text.lower()

    # category
    if "pothole" in text_lower:
        category = "Pothole"
    elif "water" in text_lower or "flood" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    else:
        category = "Other"

    # priority
    if any(word in text_lower for word in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = f"Detected keywords in complaint: {text[:30]}"
    flag = ""

    return category, priority, reason, flag


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    with open(args.input, 'r') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    output = []

    for row in rows:
        text = row[0]
        category, priority, reason, flag = classify(text)
        output.append([text, category, priority, reason, flag])

    with open(args.output, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(output)


if __name__ == "__main__":
    main()
