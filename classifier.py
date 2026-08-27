import csv
import argparse

def classify(text):
    text = text.lower()

    if "refund" in text or "money" in text:
        return "Billing"
    elif "error" in text or "issue" in text:
        return "Technical"
    elif "delay" in text or "late" in text:
        return "Service"
    else:
        return "General"


def batch_classify(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            # write header
            writer.writerow(["text", "category"])

            for row in reader:
                text = list(row.values())[0]   # safe reading
                category = classify(text)

                writer.writerow([text.strip(), category])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)