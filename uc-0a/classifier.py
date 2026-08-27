import csv
import argparse

def classify(text):

    text = text.lower()

    if "injury" in text or "hospital" in text or "child" in text:
        return "critical"

    elif "accident" in text or "danger" in text:
        return "high"

    elif "broken" in text or "pothole" in text:
        return "medium"

    else:
        return "low"


def batch_classify(input_file, output_file):

    with open(input_file, "r") as f:
        reader = csv.reader(f)

        with open(output_file, "w", newline="") as out:
            writer = csv.writer(out)

            writer.writerow(["complaint", "severity"])

            for row in reader:
                complaint = row[0]
                severity = classify(complaint)
                writer.writerow([complaint, severity])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)