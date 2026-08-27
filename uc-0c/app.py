import csv
import argparse

def process_budget(input_file, output_file):

    with open(input_file, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    process_budget(args.input, args.output)

if __name__ == "__main__":
    main()
