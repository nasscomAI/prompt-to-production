import argparse
import csv

urgent_keywords = [
    "flood",
    "ambulance",
    "risk",
    "hospital",
    "hospitalised",
    "dengue",
    "blocked",
    "collapsed",
    "crater",
    "accident",
]
def classify_complaint(row):
    complaint_id = row.get("complaint_id", "")
    text = row.get("description", "").lower()

    for word in urgent_keywords:
        if word in text:
            return {
                "complaint_id": complaint_id,
                "category": "Safety",
                "priority": "Urgent",
                "reason": f"keyword detected: {word}",
                "flag": ""
            }

    return {
        "complaint_id": complaint_id,
        "category": "General",
        "priority": "Normal",
        "reason": "no danger keywords",
        "flag": ""
    }


def batch_classify(input_path, output_path):

    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            results.append(classify_complaint(row))

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print("Done. Results written to", args.output)