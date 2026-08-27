import csv
import argparse

def classify(text):
    text = text.lower()

    if "garbage" in text or "waste" in text:
        category = "Waste Management"
    elif "road" in text or "pothole" in text:
        category = "Roads & Pothole Repair"
    elif "water" in text or "drain" in text:
        category = "Drainage & Flooding"
    else:
        category = "Other"

    if any(word in text for word in ["hospital", "school", "child", "accident"]):
        severity = "High"
    elif any(word in text for word in ["delay", "issue", "problem"]):
        severity = "Medium"
    else:
        severity = "Low"

    return category, severity


def batch_classify(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        with open(output_file, 'w', newline='', encoding='utf-8') as out:
            writer = csv.writer(out)
            writer.writerow(["Complaint", "Category", "Severity"])

            for row in reader:
                if not row:
                    continue

                complaint = row[0]
                category, severity = classify(complaint)
                writer.writerow([complaint, category, severity])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    batch_classify(args.input, args.output)

    print("Classification completed!")