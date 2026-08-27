"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import csv
import argparse

def classify(text):
    text = text.lower()

    if "water" in text:
        return "Water"
    elif "garbage" in text or "trash" in text:
        return "Sanitation"
    elif "road" in text:
        return "Road"
    else:
        return "Other"

def batch_classify(input_file, output_file):
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Complaint", "Category"])

        for row in data:
            category = classify(row[0])
            writer.writerow([row[0], category])

    print("Classification completed. Output saved to", output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)