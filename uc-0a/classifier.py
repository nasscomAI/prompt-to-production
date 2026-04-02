import csv
import argparse

def classify(text):
    text = text.lower()

    category = "Other"
    severity = "Low"

    if "garbage" in text or "waste" in text or "trash" in text:
        category = "Sanitation"
    elif "road" in text or "pothole" in text:
        category = "Road"
    elif "water" in text or "leak" in text:
        category = "Water"

    if "school" in text or "hospital" in text or "child" in text:
        severity = "High"
    elif "many" in text or "serious" in text:
        severity = "Medium"

    return category, severity


def batch_classify(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header + ["Category", "Severity"])

            for row in reader:
                text = row[0]
                category, severity = classify(text)
                writer.writerow(row + [category, severity])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print("Done. Output saved to:", args.output)