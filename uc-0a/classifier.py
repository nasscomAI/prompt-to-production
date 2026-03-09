"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    raise NotImplementedError("Build this using your AI tool + RICE prompt")


import csv
import argparse


def classify(text):

    text = text.lower()

    if "pothole" in text or "road" in text:
        return "Road"

    elif "water" in text or "leak" in text:
        return "Water"

    elif "garbage" in text or "trash" in text:
        return "Garbage"

    elif "electricity" in text or "power" in text:
        return "Electricity"

    else:
        return "Other"


def batch_classify(input_file, output_file):

    rows = []

    with open(input_file) as f:

        reader = csv.DictReader(f)

        for row in reader:

            complaint = row.get("complaint", "")

            category = classify(complaint)

            row["category"] = category

            rows.append(row)

    with open(output_file, "w", newline="") as f:

        writer = csv.DictWriter(f, fieldnames=rows[0].keys())

        writer.writeheader()

        writer.writerows(rows)

    print("Classification finished")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
