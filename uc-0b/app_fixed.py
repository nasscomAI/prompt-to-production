import csv
import argparse

def classify_text(text):
    text = text.lower()
    if "leave" in text:
        return "HR Policy"
    elif "computer" in text or "internet" in text:
        return "IT Policy"
    elif "reimbursement" in text or "expense" in text:
        return "Finance Policy"
    else:
        return "General"

def batch_process(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Text", "Category"])
            for row in reader:
                if len(row) == 0:
                    continue
                category = classify_text(row[0])
                writer.writerow([row[0], category])

# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    # !!! All lines under this MUST be indented with 4 spaces
    parser = argparse.ArgumentParser(description="UC-0B CSV classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    batch_process(args.input, args.output)
    print(f"✅ Output generated: {args.output}")